from uuid import uuid4

from sqlalchemy import create_engine
from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, Boolean

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

engine = None
SessionNoAutocommit = None
Base = declarative_base()


def open_or_create_db(path=SQLALCHEMY_DATABASE_URL):
    global engine
    global SessionNoAutocommit
    engine = create_engine(path, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionNoAutocommit = sessionmaker(
        autocommit=False, autoflush=False, bind=engine)
    return engine


@contextmanager
def get_session(readonly=False):
    global SessionNoAutocommit
    factory = SessionNoAutocommit
    session = factory()
    try:
        yield session
        if not readonly:
            session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True, index=True)
    credits = Column(Integer, default=0)
    email_qr_codes = Column(Boolean, default=False)
    registration_uuid = Column(String, unique=True)


def get_user_by_email(email: str):
    with get_session(readonly=True) as session:
        return session.query(User).filter_by(email=email).first()


def get_user_by_registration_uuid(registration_uuid: str):
    with get_session(readonly=True) as session:
        return session.query(User).filter_by(
            registration_uuid=registration_uuid).first()


def register_user(email: str, credits=0, email_qr_codes=False):
    with get_session() as session:
        session.add(User(email=email, credits=credits,
                         email_qr_codes=email_qr_codes,
                         registration_uuid=str(uuid4())))


def decrease_user_credits(email: str, amount: int) -> None:
    with get_session() as session:
        user = session.query(User).filter_by(email=email).first()
        assert (user.credits >= amount)
        user.credits -= amount


class AnonSession(Base):
    __tablename__ = "anon_session"

    id = Column(String, primary_key=True, index=True)
    credits = Column(Integer, default=0)


def decrease_anon_session_credits(visitor_id: str, amount: int) -> None:
    with get_session() as session:
        anon_session = session.query(
            AnonSession).filter_by(id=visitor_id).first()
        assert (anon_session.credits >= amount)
        anon_session.credits -= amount


def get_or_register_anon_session(visitor_id: str, credits=0) -> AnonSession:
    with get_session() as session:
        if session.query(AnonSession).filter_by(id=visitor_id).first() is None:
            session.add(AnonSession(id=visitor_id, credits=credits))
    with get_session(readonly=True) as session:
        return session.query(AnonSession).filter_by(id=visitor_id).first()


def register_anon_session(visitor_id: str, credits=0) -> None:
    with get_session() as session:
        session.add(AnonSession(id=visitor_id, credits=credits))


class QRCodeGeneration(Base):
    __tablename__ = "qrcode_generation"

    qr_code_content = Column(String, primary_key=True)
    prompt = Column(String, primary_key=True)
    negative_prompt = Column(String, primary_key=True)
    strength = Column(Integer, primary_key=True)
    guidance_scale = Column(Integer, primary_key=True)
    controlnet_conditioning_scale = Column(Integer, primary_key=True)
    num_inference_steps = Column(Integer, primary_key=True)
    seed = Column(Integer, primary_key=True)
    image_path = Column(String, unique=True)


def get_qrcode_generation(qr_code_content, prompt, negative_prompt, strength,
                          guidance_scale, controlnet_conditioning_scale,
                          num_inference_steps, seed) -> QRCodeGeneration:
    with get_session(readonly=True) as session:
        return session.query(QRCodeGeneration).filter_by(
            qr_code_content=qr_code_content,
            prompt=prompt,
            negative_prompt=negative_prompt,
            strength=strength,
            guidance_scale=guidance_scale,
            controlnet_conditioning_scale=controlnet_conditioning_scale,
            num_inference_steps=num_inference_steps,
            seed=seed).first()


def create_qrcode_generation(qr_code_content, prompt, negative_prompt, strength,
                             guidance_scale, controlnet_conditioning_scale,
                             num_inference_steps, seed, image_path):
    with get_session() as session:
        session.add(QRCodeGeneration(qr_code_content=qr_code_content,
                                     prompt=prompt,
                                     negative_prompt=negative_prompt,
                                     strength=strength,
                                     guidance_scale=guidance_scale,
                                     controlnet_conditioning_scale=controlnet_conditioning_scale,
                                     num_inference_steps=num_inference_steps,
                                     seed=seed,
                                     image_path=image_path))


#     BASE_CONFIG = {
#       "qr_code_content": "https://www.example.com",
#       "prompt": "Girl with beautiful dress, in front of majestic mountain view landscape",
#       "negative_prompt": "ugly, disfigured, low quality, blurry, nsfw, plain, mangled, weird",
#       "strength": 0.95,
#       "guidance_scale": 7.5,
#       "controlnet_conditioning_scale": 1.4,
#       "num_inference_steps": 40,
#       "seed": 2313123,
# }
