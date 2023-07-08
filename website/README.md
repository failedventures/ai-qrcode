## Development

Prompt for ChatGPT:

```
You are an experienced full-stack developer with 10 years of experience. You are building a website using the following tech stack:
- Python with FastAPI framework for the server.
- HTML templates using jinja. In addition, you use Bootstrap v5 for CSS components (e.g., for buttons, modals, etc.).

```

Then add your prompt.

## Build

### Backend

1. Install dependencies:

    ```sh
    pip install --user -r backend/requirements.txt
    ```

1. (ONCE) Add binary path to PATH:

    ```sh
    # For bash
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    source ~/.bashrc

    # For zsh
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
    source ~/.zshrc
    ```

## Run Website Locally

1. Export the RunPod API key and endpoint as environment variables:

    ```sh
    export RUNPOD_ENDPOINT="36sv4p6lwum0sq"
    export RUNPOD_API_TOKEN="..."
    ```

1. Run the backend:

    ```sh
    make run-backend
    ```

1. Open the website at [http://localhost:8000](http://localhost:8000).

## QR-Code Generation API

We use a serverless GPU provider to host our QRCore generation model.
We tried Replicate and RunPod, and the latter has much better latency and
price.

### Build RunPod image

#### Prepare the machine (Lambda Labs)

1. Create a new A100 machine from the UI. It will also ask for a public key.

1. Copy `ai-qrcode` repo to the remote machine:

    ```sh
    export MACHINE="<ip from Lambda Labs UI>"
    export REPO_PATH="$HOME/Desktop/ai-qrcode"
    rsync -r -avpl --delete $REPO_PATH/QR-code-AI-art-generator ubuntu@$MACHINE:~/
    ```

1. SSH into the machine:

    ```sh
    ssh ubuntu@$MACHINE
    ```

1. Add user to docker group, exit ssh session and connect again:

    ```sh
    sudo usermod -aG docker ubuntu
    exit
    ssh ubuntu@$MACHINE
    ```

#### Build and Push Image

1. Build the container:

    ```sh
    cd ~/QR-code-AI-art-generator
    docker build -t ai-qrcode-runpod:latest -f Dockerfile.runpod .
    ```

1. Download model weights:

    ```sh
    docker run -it -v "$(pwd)":/model --gpus=all ai-qrcode-runpod:latest python3 runpod_predict.py
    ```

1. Build image again:

    ```sh
    docker build -t ai-qrcode-runpod:latest -f Dockerfile.runpod .
    ```

1. Get a personal access token from GitHub with write package access.

1. Push to GitHub packages:

    ```sh
    GH_USERNAME="failedventures"
    DOCKER_IMAGE="ghcr.io/${GH_USERNAME}/ai-qrcode-runpod:01492d3ef0760442ca11b97fef8a144dcc2c601c"

    CR_PAT="<github api token>"
    echo $CR_PAT | docker login ghcr.io -u USERNAME --password-stdin
    docker tag ai-qrcode-runpod:latest $DOCKER_IMAGE
    docker push $DOCKER_IMAGE
    ```


### Build replicate image

Follow the prepare section from the cloud you're using!

#### Prepare the machine (Google Cloud)

Prerequisites:
- You need to upgrade to a paid account to use GPUs. This is just a matter of
  clicking a button.
- You need to update the quota of A100, by default it's zero.

1. Create gcloud machine (use the A100 command):

    ```sh
    # For A100
    gcloud compute instances create replicate-builder \
        --project=neon-camp-385707 \
        --zone=us-central1-a \
        --machine-type=a2-highgpu-1g \
        --network-interface=network-tier=PREMIUM,stack-type=IPV4_ONLY,subnet=default \
        --maintenance-policy=TERMINATE \
        --provisioning-model=STANDARD \
        --service-account=411204257049-compute@developer.gserviceaccount.com \
        --scopes=https://www.googleapis.com/auth/devstorage.read_only,https://www.googleapis.com/auth/logging.write,https://www.googleapis.com/auth/monitoring.write,https://www.googleapis.com/auth/servicecontrol,https://www.googleapis.com/auth/service.management.readonly,https://www.googleapis.com/auth/trace.append \
        --accelerator=count=1,type=nvidia-tesla-a100 \
        --create-disk=auto-delete=yes,boot=yes,device-name=instance-1,image=projects/ml-images/global/images/c0-deeplearning-common-cpu-v20230615-debian-10,mode=rw,size=500,type=projects/neon-camp-385707/zones/us-west4-b/diskTypes/pd-ssd \
        --no-shielded-secure-boot \
        --shielded-vtpm \
        --shielded-integrity-monitoring \
        --labels=goog-ec-src=vm_add-gcloud \
        --reservation-affinity=any
    ```

    ```sh
    # For T4
    gcloud compute instances create replicate-builder \
        --project=neon-camp-385707 \
        --zone=us-west4-b \
        --machine-type=n1-standard-16 \
        --network-interface=network-tier=PREMIUM,stack-type=IPV4_ONLY,subnet=default \
        --maintenance-policy=TERMINATE \
        --provisioning-model=STANDARD \
        --service-account=411204257049-compute@developer.gserviceaccount.com \
        --scopes=https://www.googleapis.com/auth/devstorage.read_only,https://www.googleapis.com/auth/logging.write,https://www.googleapis.com/auth/monitoring.write,https://www.googleapis.com/auth/servicecontrol,https://www.googleapis.com/auth/service.management.readonly,https://www.googleapis.com/auth/trace.append \
        --accelerator=count=1,type=nvidia-tesla-t4 \
        --create-disk=auto-delete=yes,boot=yes,device-name=replicate-builder,image=projects/ml-images/global/images/c2-deeplearning-pytorch-1-10-cu110-v20220227-debian-10,mode=rw,size=500,type=projects/neon-camp-385707/zones/us-west4-b/diskTypes/pd-ssd \
        --no-shielded-secure-boot \
        --shielded-vtpm \
        --shielded-integrity-monitoring \
        --labels=goog-ec-src=vm_add-gcloud \
        --reservation-affinity=any
    ```

2. Configure SSH:

    ```sh
    gcloud compute config-ssh
    ```

3. Copy `ai-qrcode` repo to the remote machine:

    ```sh
    export NAME="replicate-builder"
    export ZONE="us-west4-b"
    export PROJECT="$(gcloud config get-value project)"
    export MACHINE="$NAME.$ZONE.$PROJECT"
    export REPO_PATH="$HOME/Desktop/ai-qrcode"
    rsync -r -avpl $REPO_PATH $MACHINE:~/
    ```

4. SSH into the machine. Click yes for drivers install. Note that it can take a
   minute or two until background install processes finish and we can install
   the drivers:

    ```sh
    ssh $MACHINE
    ```

5. Install Docker:

    ```sh
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io \
        docker-buildx-plugin docker-compose-plugin
    ```

6. Install latest NVIDIA drivers and remove existing ones:

    ```sh
    # From: https://developer.nvidia.com/cuda-downloads?target_os=Linux&target_arch=x86_64&Distribution=Debian&target_version=10&target_type=deb_network
    wget https://developer.download.nvidia.com/compute/cuda/repos/debian10/x86_64/cuda-keyring_1.0-1_all.deb
    sudo dpkg -i cuda-keyring_1.0-1_all.deb
    sudo add-apt-repository contrib
    sudo apt-get update
    sudo apt-get -y install cuda
    ```

#### Prepare the machine (Lambda Labs)

1. Create a new A100 machine from the UI. It will also ask for a public key.

1. Copy `ml-experiments` repo to the remote machine:

    ```sh
    export MACHINE="<ip from Lambda Labs UI>"
    export REPO_PATH="$HOME/Desktop/ai-qrcode"
    rsync -r -avpl --delete $REPO_PATH/QR-code-AI-art-generator ubuntu@$MACHINE:~/
    ```

1. SSH into the machine:

    ```sh
    ssh ubuntu@$MACHINE
    ```

1. Add user to docker group, exit ssh session and connect again:

    ```sh
    sudo usermod -aG docker ubuntu
    exit
    ssh ubuntu@$MACHINE
    ```

#### Build and Push Image

1. Create a new model page on replicate (https://replicate.com/create). Or use
   an existing one if you have it. For example, use the name `ai-qrcode`.

1. Install Cog:

    ```sh
    sudo curl -o /usr/local/bin/cog -L https://github.com/replicate/cog/releases/latest/download/cog_`uname -s`_`uname -m`
    sudo chmod +x /usr/local/bin/cog
    ```

1. Build image:

    ```sh
    cd ~/ai-qrcode/QR-code-AI-art-generator/
    cog run python3 hg_model_download.py
    cog build
    ```

1. Run test inference:

    ```sh
    cog predict \
        -i qr_code_content="example.com" \
        -i prompt="top view of city with skyscrapers" \
        -i negative_prompt="ugly, disfigured"
    ```

1. Upload to replicate:

    ```sh
    USERNAME="..."
    MODEL_NAME="ai-qrcode"  # this is the replicated model you created earlier
    cog login
    cog push r8.im/$USERNAME/$MODEL_NAME
    ```
