MODEL_LIST = [

    # =======================================================
    # 1. MAIN DIFFUSION MODEL (FLUX 2 KLEIN)
    # =======================================================
    {
        "url": "https://huggingface.co/black-forest-labs/FLUX.2-klein-9B/resolve/main/flux-2-klein-9b.safetensors",
        "path": "/data/models/unet/flux-2-klein-9b.safetensors",
        "target": "/comfyui/models/unet/flux-2-klein-9b.safetensors"
    },

    # =======================================================
    # 2. VAE FOR FLUX 2
    # =======================================================
    {
        "url": "https://huggingface.co/Comfy-Org/flux2-dev/resolve/main/split_files/vae/flux2-vae.safetensors",
        "path": "/data/models/vae/flux2-vae.safetensors",
        "target": "/comfyui/models/vae/flux2-vae.safetensors"
    },

    # =======================================================
    # 3. CLIP MODEL FOR FLUX 2
    # =======================================================
    {
        "url": "https://huggingface.co/Comfy-Org/flux2-klein-9B/resolve/main/split_files/text_encoders/qwen_3_8b_fp8mixed.safetensors",
        "path": "/data/models/clip/qwen_3_8b_fp8mixed.safetensors",
        "target": "/comfyui/models/clip/qwen_3_8b_fp8mixed.safetensors"
    },

    # =======================================================
    # 4. LORA MODEL (NSFW)
    # =======================================================
    {
        "url": "https://huggingface.co/kirusanth08/flux_klein_nsfw_v2/resolve/main/Flux%20Klein%20-%20NSFW%20v2.safetensors",
        "path": "/data/models/loras/Flux Klein - NSFW v2.safetensors",
        "target": "/comfyui/models/loras/Flux Klein - NSFW v2.safetensors"
    }
]
