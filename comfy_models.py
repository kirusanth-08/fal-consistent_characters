MODEL_LIST = [

    # =======================================================
    # 1. MAIN DIFFUSION MODEL (QWEN-IMAGE-EDIT)
    # =======================================================
    {
        "url": "https://huggingface.co/Comfy-Org/Qwen-Image-Edit_ComfyUI/resolve/main/split_files/diffusion_models/qwen_image_edit_2509_fp8_e4m3fn.safetensors",
        "path": "/data/models/diffusion_models/Qwen-Image-Edit-2509_fp8_e4m3fn.safetensors",
        "target": "/comfyui/models/diffusion_models/Qwen-Image-Edit-2509_fp8_e4m3fn.safetensors"
    },

    # =======================================================
    # 2. VAE FOR QWEN-IMAGE MODEL
    # =======================================================
    {
        "url": "https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/vae/qwen_image_vae.safetensors",
        "path": "/data/models/vae/qwen_image_vae.safetensors",
        "target": "/comfyui/models/vae/qwen_image_vae.safetensors"
    },

    # =======================================================
    # 3. CLIP MODELS FOR QWEN-IMAGE MODEL
    # =======================================================
    {
        "url": "https://huggingface.co/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/text_encoders/qwen_2.5_vl_7b.safetensors",
        "path": "/data/models/text_encoders/qwen_2.5_vl_7b.safetensors",
        "target": "/comfyui/models/text_encoders/qwen_2.5_vl_7b.safetensors"
    },

    # =======================================================
    # 4. LORA MODELS FOR QWEN-MULTI-LIGHTING MODEL
    # =======================================================
    {
        "url": "https://huggingface.co/lightx2v/Qwen-Image-Lightning/resolve/main/Qwen-Image-Lightning-8steps-V2.0.safetensors",
        "path": "/data/models/loras/Qwen-Image-Lightning-8steps-V2.0.safetensors",
        "target": "/comfyui/models/loras/Qwen-Image-Lightning-8steps-V2.0.safetensors"
    },
    {
        "url": "https://huggingface.co/spaces/lllyasviel/IC-Light/resolve/main/models/iclight_sd15_fc.safetensors",
        "path": "/data/models/loras/iclight_sd15_fc.safetensors",
        "target": "/comfyui/models/loras/iclight_sd15_fc.safetensors"
    }
]
