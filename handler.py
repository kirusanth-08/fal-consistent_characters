import fal
from fal.container import ContainerImage
from fal.toolkit import Image
from fastapi import Request, Response
from pathlib import Path
import json
import uuid
import base64
import requests
import websocket
import traceback
import os
import copy
import random
import tempfile
from io import BytesIO
from PIL import Image as PILImage
from pydantic import BaseModel, Field
from typing import Literal
from comfy_models import MODEL_LIST
from workflow import WORKFLOW_JSON

# -------------------------------------------------
# Container setup
# -------------------------------------------------
PWD = Path(__file__).resolve().parent
dockerfile_path = f"{PWD}/Dockerfile"
custom_image = ContainerImage.from_dockerfile(dockerfile_path)

COMFY_HOST = "127.0.0.1:8188"

# -------------------------------------------------
# Resolution Presets
# -------------------------------------------------
RESOLUTION_PRESETS = {
    "hd": {"width": 720, "height": 1280},
    "square": {"width": 1024, "height": 1024},
    "squareHD": {"width": 2048, "height": 2048},
    "portrait_3_4": {"width": 1536, "height": 2048},
    "portrait_9_16": {"width": 1152, "height": 2048},
    "landscape_16_9": {"width": 2048, "height": 1152},
    "landscape_4_3": {"width": 2048, "height": 1536}
}


# -------------------------------------------------
# Utilities
# -------------------------------------------------
def ensure_dir(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

def download_if_missing(url, path):
    if os.path.exists(path):
        return
    ensure_dir(path)
    
    # Add Hugging Face authentication if HF_TOKEN_k is available
    headers = {}
    hf_token = os.environ.get("HF_TOKEN_k") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    if hf_token and "huggingface.co" in url:
        headers["Authorization"] = f"Bearer {hf_token}"
    
    with requests.get(url, stream=True, headers=headers) as r:
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)

def check_server(url, retries=500, delay=0.1):
    import time
    for _ in range(retries):
        try:
            if requests.get(url).status_code == 200:
                return True
        except:
            pass
        time.sleep(delay)
    return False

def fal_image_to_base64(img: Image) -> str:
    pil = img.to_pil()
    buf = BytesIO()
    pil.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()

def image_url_to_base64(image_url: str) -> str:
    """Download image from URL and convert to base64."""
    response = requests.get(image_url)
    response.raise_for_status()
    pil = PILImage.open(BytesIO(response.content))
    buf = BytesIO()
    pil.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()

def upload_images(images):
    for img in images:
        blob = base64.b64decode(img["image"])
        files = {"image": (img["name"], BytesIO(blob), "image/png")}
        r = requests.post(f"http://{COMFY_HOST}/upload/image", files=files)
        r.raise_for_status()

def apply_fixed_values(workflow: dict, seed_value: int):
    for node in workflow.values():
        inputs = node.get("inputs", {})

        # Update RandomNoise node seed
        if node.get("class_type") == "RandomNoise":
            inputs["noise_seed"] = seed_value

# -------------------------------------------------
# Input Model
# -------------------------------------------------
class CharacterInput(BaseModel):
    prompt: str = Field(
        ...,
        title="Prompt",
        description="Text prompt for the image generation.",
        examples=[
            "This character sitting on a modern office chair in a bright workspace",
            "Make this person on the image standing on a ground between flower plants",
            "The person walking on a beach during sunset with waves in the background",
            "This individual standing in front of a futuristic cityscape at night",
            "The character posing in a studio with professional lighting and white background",
            "This person in a cozy coffee shop reading a book by the window"
        ]
    )
    image_url: str = Field(
        ...,
        title="Input Image",
        description="URL of the character image to process.",
        examples=[
            "https://media.istockphoto.com/id/1442495175/photo/beauty-portrait-and-natural-face-of-black-woman-with-healthy-freckle-skin-texture-touch.jpg?s=612x612&w=0&k=20&c=DhKsXATpL5BZbBrSta3O7k2ob4K7yD01zHeKyIZU5XI=",
            "https://img.freepik.com/free-photo/sensual-woman-looking-front_197531-19790.jpg?semt=ais_hybrid&w=740&q=80",
        ]
    )
    seed: int = Field(
        default_factory=lambda: random.randint(0, 2**32 - 1),
        title="Seed",
        description="Random seed for reproducible generation. Use the same seed for consistent results."
    )
    resolution: Literal[
        "hd",
        "square",
        "squareHD",
        "portrait_3_4",
        "portrait_9_16",
        "landscape_16_9",
        "landscape_4_3"
    ] = Field(
        default="square",
        title="Resolution Preset",
        description="Choose from preset resolutions: hd (720×1280), square (1024×1024), squareHD (2048×2048), portrait_3_4 (1536×2048), portrait_9_16 (1152×2048), landscape_16_9 (2048×1152), landscape_4_3 (2048×1536)",
    )
    nsfw: bool = Field(
        default=False,
        title="NSFW Mode",
        description="Enable NSFW content generation. If false, NSFW LoRA strength is set to 0."
    )

# -------------------------------------------------
# Output Model
# -------------------------------------------------
class CharacterOutput(BaseModel):
    """Output model for character generation."""
    image: Image = Field(
        description="The generated image file info.",
        examples=[
            Image(
                url="https://fal.media/files/example/character.png",
                width=1024,
                height=1024,
                content_type="image/png",
            )
        ],
    )
    seed: int = Field(
        description="Seed of the generated image. Same value as input or randomly generated."
    )
    prompt: str = Field(
        description="The prompt used for generating the image."
    )

# -------------------------------------------------
# App - NEW FORMAT with parameters in class declaration
# -------------------------------------------------
class KoraEdit(
    fal.App,
    keep_alive=300,
    min_concurrency=0,
    max_concurrency=5,
):
    """Character Generator - Generate character images with Flux 2 Klein model."""
    
    image = custom_image
    machine_type = "GPU-H100"
    requirements = ["websockets", "websocket-client"]

    # 🔒 CRITICAL
    private_logs = True

    def setup(self):
        # Print GPU info
        try:
            import subprocess
            gpu_info = subprocess.check_output(
                ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                text=True
            ).strip()
            print(f"🖥️ GPU Type: {gpu_info}")
        except Exception as e:
            print(f"⚠️ Could not detect GPU: {e}")

        # Download models
        for model in MODEL_LIST:
            download_if_missing(model["url"], model["path"])

        # Symlink models
        for model in MODEL_LIST:
            ensure_dir(model["target"])
            if not os.path.exists(model["target"]):
                os.symlink(model["path"], model["target"])

        # Start ComfyUI (NO --log-stdout)
        import subprocess
        self.comfy = subprocess.Popen(
            [
                "python", "-u", "/comfyui/main.py",
                "--disable-auto-launch",
                "--disable-metadata",
                "--listen", "--port", "8188"
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        if not check_server(f"http://{COMFY_HOST}/system_stats"):
            raise RuntimeError("ComfyUI failed to start")

    @fal.endpoint("/")
    async def generate(
        self, 
        input: CharacterInput, 
        response: Response
    ) -> CharacterOutput:
        """Generate character image based on input parameters."""
        try:
            job = copy.deepcopy(WORKFLOW_JSON)
            workflow = job["input"]["workflow"]

            input_img = f"input_{uuid.uuid4().hex}.png"

            upload_images([
                {"name": input_img, "image": image_url_to_base64(input.image_url)}
            ])

            # Update workflow with input image (node 125)
            workflow["125"]["inputs"]["image"] = input_img

            # Update prompt (node 119)
            workflow["119"]["inputs"]["text"] = input.prompt

            # Update seed (node 109)
            workflow["109"]["inputs"]["noise_seed"] = input.seed

            # Get width and height from resolution preset (node 102)
            resolution = RESOLUTION_PRESETS[input.resolution]
            workflow["102"]["inputs"]["width"] = resolution["width"]
            workflow["102"]["inputs"]["height"] = resolution["height"]

            # Update NSFW LoRA strength (node 116)
            lora_strength = 1.0 if input.nsfw else 0.0
            workflow["116"]["inputs"]["strength_model"] = lora_strength

            # Run ComfyUI
            client_id = str(uuid.uuid4())
            ws = websocket.WebSocket()
            ws.connect(f"ws://{COMFY_HOST}/ws?clientId={client_id}")

            resp = requests.post(
                f"http://{COMFY_HOST}/prompt",
                json={"prompt": workflow, "client_id": client_id},
                timeout=30
            )
            
            # Log detailed error if request fails
            if resp.status_code != 200:
                error_detail = resp.text
                print(f"ComfyUI Error Response: {error_detail}")
                return {"error": f"ComfyUI rejected workflow: {error_detail}"}
            
            prompt_id = resp.json()["prompt_id"]

            while True:
                out = ws.recv()
                # Ensure proper decoding: handle both string and bytes
                if isinstance(out, bytes):
                    out = out.decode('utf-8')
                
                # Skip empty messages or non-JSON text (progress updates, debug info)
                if not out or not out.strip():
                    continue
                
                # Only process JSON messages, silently skip text messages
                if not out.strip().startswith('{'):
                    continue
                
                try:
                    msg = json.loads(out)
                except json.JSONDecodeError:
                    # Skip malformed messages without logging
                    continue
                
                if msg.get("type") == "executing" and msg["data"]["node"] is None:
                    break

            history = requests.get(
                f"http://{COMFY_HOST}/history/{prompt_id}"
            ).json()

            # Get the first image from outputs
            output_image = None
            for node in history[prompt_id]["outputs"].values():
                for img in node.get("images", []):
                    params = (
                        f"filename={img['filename']}"
                        f"&subfolder={img.get('subfolder','')}"
                        f"&type={img['type']}"
                    )
                    r = requests.get(f"http://{COMFY_HOST}/view?{params}")
                    # Convert to PIL Image and use Image.from_pil (modern fal toolkit pattern)
                    pil_image = PILImage.open(BytesIO(r.content))
                    output_image = Image.from_pil(pil_image, format="png")
                    break
                if output_image:
                    break

            ws.close()
            
            # Set billing units based on resolution
            resolution = RESOLUTION_PRESETS[input.resolution]
            resolution_factor = (resolution["width"] * resolution["height"]) / (1024 * 1024)
            response.headers["x-fal-billable-units"] = str(int(resolution_factor))
            
            return CharacterOutput(
                image=output_image, 
                seed=input.seed,
                prompt=input.prompt
            )

        except Exception as e:
            traceback.print_exc()
            # Re-raise as HTTPException for proper error handling
            from fastapi import HTTPException
            raise HTTPException(status_code=500, detail=str(e))
