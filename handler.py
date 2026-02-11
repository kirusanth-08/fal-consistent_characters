import fal
from fal.container import ContainerImage
from fal.toolkit.image import Image
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
# Utilities
# -------------------------------------------------
def ensure_dir(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

def download_if_missing(url, path):
    if os.path.exists(path):
        return
    ensure_dir(path)
    with requests.get(url, stream=True) as r:
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

        if node.get("class_type") == "KSampler":
            inputs["seed"] = seed_value

# -------------------------------------------------
# Light Position Mapping
# -------------------------------------------------
LIGHT_POSITION_MAP = {
    "below": "below",
    "ahead": "ahead",
    "left": "the left",
    "rear": "the rear",
    "right_rear": "the right rear",
    "left_rear": "the left rear"
}

from typing import Literal

LightPosition = Literal[
    "below", "ahead", "left", "rear", "right_rear",
    "left_rear"
]

# -------------------------------------------------
# Input Model (ONLY image inputs in UI)
# -------------------------------------------------
class LightPatternInput(BaseModel):
    main_image_url: str = Field(
        ...,
        title="Main Image",
        description="URL of the main image to process.",
        examples=[
            "https://images.unsplash.com/photo-1707661553213-df6e18dd54ad?fm=jpg&q=60&w=3000&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1yZWxhdGVkfDExfHx8ZW58MHx8fHx8",
            "https://images.pexels.com/photos/5077664/pexels-photo-5077664.jpeg?auto=compress&cs=tinysrgb&dpr=1&w=500"
        ]
    )
    reference_image_url: str = Field(
        ...,
        title="Reference Image",
        description="URL of the reference image for lighting.",
        examples=[
            "https://images.unsplash.com/photo-1712249363853-47098b4a62ae?fm=jpg&q=60&w=3000&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1yZWxhdGVkfDE1fHx8ZW58MHx8fHx8"
        ]
    )
    light_position: LightPosition = Field(
        title="Light Position",
        description="The direction of the light source.",
    )

# -------------------------------------------------
# App
# -------------------------------------------------
class LightPattern(fal.App):
    """Light Pattern - Dynamic image relighting with customizable light positions."""
    
    # Optional: Set explicit app metadata
    title = "Light Pattern"
    description = "Dynamic image relighting with customizable light positions"

    image = custom_image
    machine_type = "GPU-H100"
    max_concurrency = 5
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
    def handler(self, input: LightPatternInput):
        try:
            job = copy.deepcopy(WORKFLOW_JSON)
            workflow = job["input"]["workflow"]

            main_img = f"main_{uuid.uuid4().hex}.png"
            ref_img = f"ref_{uuid.uuid4().hex}.png"

            upload_images([
                {"name": main_img, "image": image_url_to_base64(input.main_image_url)},
                {"name": ref_img, "image": image_url_to_base64(input.reference_image_url)}
            ])

            workflow["31"]["inputs"]["image"] = main_img
            workflow["7"]["inputs"]["image"] = ref_img

            # Update prompt with light position
            light_direction = LIGHT_POSITION_MAP.get(input.light_position, "the front")
            prompt = f"Relight Figure 1 using the brightness map from Figure 2 (light source from {light_direction})"
            workflow["11"]["inputs"]["prompt"] = prompt

            seed_value = random.randint(0, 2**63 - 1)
            apply_fixed_values(workflow, seed_value)

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
                msg = json.loads(ws.recv())
                if msg.get("type") == "executing" and msg["data"]["node"] is None:
                    break

            history = requests.get(
                f"http://{COMFY_HOST}/history/{prompt_id}"
            ).json()

            images = []
            for node in history[prompt_id]["outputs"].values():
                for img in node.get("images", []):
                    params = (
                        f"filename={img['filename']}"
                        f"&subfolder={img.get('subfolder','')}"
                        f"&type={img['type']}"
                    )
                    r = requests.get(f"http://{COMFY_HOST}/view?{params}")
                    # Save to temp file and use Image.from_path for better compatibility
                    temp_path = f"/tmp/output_{uuid.uuid4().hex}.png"
                    with open(temp_path, "wb") as f:
                        f.write(r.content)
                    try:
                        images.append(Image.from_path(temp_path))
                    except Exception as upload_err:
                        print(f"Image upload warning: {upload_err}")
                        # Fallback: try with explicit repository parameter
                        images.append(Image.from_path(temp_path, repository="cdn"))

            ws.close()
            return {"status": "success", "images": images}

        except Exception as e:
            traceback.print_exc()
            return {"error": str(e)}
