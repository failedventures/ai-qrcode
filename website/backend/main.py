import os
import sys
import http
import uuid
import time
import logging
import database
from typing import Sequence
from pydantic import BaseModel
from email_api import send_email
from typing import Set, Annotated
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request, Response, Header
from fastapi.responses import JSONResponse, HTMLResponse
from qrcode_gen_api import qrcode_gen_runpod as qrcode_gen, setup_runpod
from email_validator import validate_email, EmailNotValidError

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


###############################################################################
# QRCode Generation API - RunPod ##############################################
###############################################################################

runpod_endpoint = os.getenv("RUNPOD_ENDPOINT")
if not runpod_endpoint:
    log.fatal("Missing RUNPOD_ENDPOINT environment variable.")
    sys.exit(1)
runpod_api_token = os.getenv("RUNPOD_API_TOKEN")
if not runpod_api_token:
    log.fatal("Missing RUNPOD_API_TOKEN environment variable.")
    sys.exit(1)
setup_runpod(endpoint=runpod_endpoint, api_token=runpod_api_token)


###############################################################################
# Email #######################################################################
###############################################################################


def load_email_list(path: str) -> Set[str]:
    with open(path, "r") as f:
        return set([line.strip() for line in f.readlines()])


def is_email_provider_blacklisted(email_provider: str) -> bool:
    return email_provider in EMAIL_BLACKLIST


EMAIL_BLACKLIST = load_email_list("disposable_email_blocklist.conf")


###############################################################################
# Website #####################################################################
###############################################################################

NEW_USER_CREDITS = 10

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

if os.getenv("DEV_MODE") == "true":
    log.info("Running in dev mode")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Database
database.open_or_create_db()

# Images
GENERATED_IMG_FOLDER = "generated_images"
os.makedirs(GENERATED_IMG_FOLDER, exist_ok=True)


###############################################################################
# Helpers #####################################################################
###############################################################################

def file_contents(path: str) -> Sequence[bytes]:
    with open(path, "rb") as f:
        return f.read()

###############################################################################
# Routes ######################################################################
###############################################################################


# The base config contains the best default settings we could find.
BASE_CONFIG = {
    "qr_code_content": "https://www.example.com",
    "prompt": "Girl with beautiful dress, in front of majestic mountain view landscape",
    "negative_prompt": "ugly, disfigured, low quality, blurry, nsfw, plain, mangled, weird",
    "strength": 0.95,
    "guidance_scale": 7.5,
    "controlnet_conditioning_scale": 1.4,
    "num_inference_steps": 40,
    "seed": 2313123,
}


class CreateQRCodeRequest(BaseModel):
    qrcode_content: str
    prompt: str


@app.post("/qrcode")
def create_qrcode(req: CreateQRCodeRequest,
                  visitor_id: Annotated[str | None, Header()],
                  registration_uuid: str = None):
    log.info("Create qrcode handler.")
    if registration_uuid:
        log.info("Got registration uuid: %s", registration_uuid)
        user = database.get_user_by_registration_uuid(registration_uuid)
        if not user:
            log.error("Couldn't find user with registration uuid: %s",
                      registration_uuid)
            return JSONResponse(status_code=http.HTTPStatus.UNAUTHORIZED,
                                content={"error": "invalid_registration_uuid",
                                         "message": "Invalid UUID."})
        if user.credits <= 0:
            log.info("No credits left for user: %s", user.email)
            return JSONResponse(status_code=http.HTTPStatus.BAD_REQUEST,
                                content={"error": "no_credits",
                                         "message": "You don't have enough credits left. Email us at <> if you need more credits."})
        database.decrease_user_credits(user.email, amount=1)
        log.info("Successfully decreased credits for user: %s", user.email)
    else:
        if not visitor_id and visitor_id != "null":
            # Handle the case when Visitor-ID is missing
            log.error("Missing visitor_id: %s", visitor_id)
            raise JSONResponse(status_code=http.HTTPStatus.UNAUTHORIZED,
                               content={"error": "missing_visitor_id",
                                        "message": "Couldn't identify user."})
        log.info("Got visitor id: %s", visitor_id)
        anon_session = database.get_or_register_anon_session(visitor_id,
                                                             credits=NEW_USER_CREDITS)
        if anon_session.credits <= 0:
            log.info("No credits left for visitor: %s", visitor_id)
            return JSONResponse(status_code=http.HTTPStatus.BAD_REQUEST,
                                content={"error": "no_credits",
                                         "message": "You don't have enough credits left. Please register your email to get more credits."})
        database.decrease_anon_session_credits(visitor_id, amount=1)
    # Check if generation already exists
    config = BASE_CONFIG.copy()
    config["qr_code_content"] = req.qrcode_content.strip()
    config["prompt"] = req.prompt.strip()
    log.info("QRCode config: %s", config)
    generation = database.get_qrcode_generation(
        qr_code_content=config["qr_code_content"],
        prompt=config["prompt"],
        negative_prompt=config["negative_prompt"],
        strength=config["strength"],
        guidance_scale=config["guidance_scale"],
        controlnet_conditioning_scale=config["controlnet_conditioning_scale"],
        num_inference_steps=config["num_inference_steps"],
        seed=config["seed"])
    if generation:
        log.info("Found existing generation: %s", generation.image_path)
        img = file_contents(os.path.join(GENERATED_IMG_FOLDER,
                                         generation.image_path))
    else:
        log.info("Creating new generation.")
        image_path = "%s.png" % uuid.uuid4()
        start_time = time.monotonic()
        img = qrcode_gen(config)
        end_time = time.monotonic()
        log.info("Generation took %.2f seconds.", end_time - start_time)
        with open(os.path.join(GENERATED_IMG_FOLDER, image_path), "wb") as f:
            f.write(img)
        database.create_qrcode_generation(
            qr_code_content=config["qr_code_content"],
            prompt=config["prompt"],
            negative_prompt=config["negative_prompt"],
            strength=config["strength"],
            guidance_scale=config["guidance_scale"],
            controlnet_conditioning_scale=config["controlnet_conditioning_scale"],
            num_inference_steps=config["num_inference_steps"],
            seed=config["seed"],
            image_path=image_path)

    return Response(content=img, media_type="image/png")


class CreateUserRequest(BaseModel):
    email: str
    email_qr_codes: bool = False


@app.post("/register_user")
def register_user_handler(req: CreateUserRequest):
    try:
        email_info = validate_email(req.email)
    except EmailNotValidError as e:
        log.error(f"Invalid email: {req.email}. Error: {e}")
        return JSONResponse(status_code=400,
                            content={"error": "invalid_email",
                                     "message": "Your email looks like it's not valid."})
    if is_email_provider_blacklisted(email_info.domain):
        log.error(f"Blacklisted email: {req.email}")
        return JSONResponse(status_code=400,
                            content={"error": "blacklisted_email",
                                     "message": "Your email provider is not supported. Please use a different email address."})
    log.info("Checking if email already exists.")
    if database.get_user_by_email(req.email):
        return JSONResponse(status_code=400,
                            content={"error": "email_already_exists",
                                     "message": "This email address is already registered."})
    log.info(f"Recording email: {req.email}")
    database.register_user(req.email, credits=NEW_USER_CREDITS,
                           email_qr_codes=req.email_qr_codes)
    send_email(req.email, "Welcome to QR Code Generator", "")
    log.info("Successfully sent email to %s", req.email)
    return Response(status_code=200)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("generator.html", {"request": request})
