# Consistent Character - Flux 2 Klein Deployment

A Docker-based deployment for character generation using Flux 2 Klein model with ComfyUI, optimized for fal.ai and featuring consistent character creation capabilities.

## Overview

This repository contains a complete deployment setup for the Flux 2 Klein model, which is a powerful character image generation system. The deployment includes:



## Quick Start

### Prerequisites

**Hugging Face Authentication** (Required for Flux models):
1. Create a Hugging Face account at https://huggingface.co
2. Accept the model license for Black Forest Labs FLUX models:
   - Visit: https://huggingface.co/black-forest-labs/FLUX.1-schnell
   - Click "Agree and access repository"
3. Create an access token:
   - Go to https://huggingface.co/settings/tokens
   - Create a new token with "Read" permissions
   - Copy the token (starts with `hf_...`)
4. Set the environment variable:
   ```bash
   export HF_TOKEN_k="hf_your_token_here"
   ```
   Or for fal.ai deployment, add it as a secret in your fal dashboard.

### Local Deployment

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd fal-consistent_characters
   ```


### Model Download
All the models downloaded must be stored in a persistent volume which in fal's case is /data
So the setup function in the handler.py takes in a MODEL_LIST and checks if it already exists in the data directory. If it does then its alright. It proceeds to symlink the models directory of the container's comfyui with the /data/models
If it does not exist in the data then it downloads the model and stores it in the data/models directory. 
To add models you need to edit the comfy_models.py file and update the list there.
It contains:
 - url: url which the code will use to download the model
 - path: the persistent volume path where the model will be downloaded
 - target: the container comfyui target where the model should be present so that comfyui can access it



## Configuration



### Workflow Configuration

The `workflow.py` contains a complete ComfyUI workflow with the format that is acceptable by the api
## Custom Nodes

The deployment includes several custom ComfyUI nodes:

- **ComfyUI-KJNodes**: Advanced node collection (GetImageSize, ImageScaleToTotalPixels, etc.)
- **ComfyUI-RunpodDirect**: Runpod integration utilities
- **Civicomfy**: CivitAI integration for model downloads
- **ComfyUI-Manager**: Custom node and model management

All these custom nodes are added using the Dockerfile. You can see how to add custom nodes in the Dockerfile. Some custom nodes don't have a requirements file so you need to skip the requirements installation part for them

## Usage

1. **Setup**: Change the model paths and urls and the custom nodes according to your workflow
2. **Authentication**: Set your HF_TOKEN_k environment variable for Hugging Face model downloads (required for FLUX models)
3. **Python Version**: The python version in the dockerfile should match the local computer. My PC uses python 3.12. So the dockerfile was modified to use python 3.12
4. **Testing**: Add the fal api key in your env and select the appropriate team. Then use the command ```fal run handler.py::CharacterGenerator``` to run the container. It will give you 3 links. Use the playground link to test your workflow.py there.
5. **Deploy**: Use ```fal deploy handler.py::CharacterGenerator``` to deploy the serverless endpoint completely. Make sure to add HF_TOKEN_k as a secret in your fal.ai dashboard.

5. **Querying Using Endpoint**: We will mostly be using the asynchronous endpoint. Once you have that endpoint you need to send request to it in this format
```POST https://queue.fal.run/YOUR_TEAM/your-app-id/```
Inside the headers you need to add the following 
```"Content-Type: application/json"``` 
```"Authorization: Key $FAL_API_KEY"```

In the body, pass your input parameters:
```json
{
  "image_url": "https://example.com/character.jpg",
  "prompt": "Make this person standing on a ground between flower plants"
}
```

Now you will get the response in this format
```json
{
    "status": "IN_QUEUE",
    "request_id": "af0b0652-d0ae-4eed-867f-167f9d970db0",
    "response_url": "https://queue.fal.run/VISIONREIMAGINE/d11f80a6-1d26-452b-bdf2-14eacd823871/requests/af0b0652-d0ae-4eed-867f-167f9d970db0",
    "status_url": "https://queue.fal.run/VISIONREIMAGINE/d11f80a6-1d26-452b-bdf2-14eacd823871/requests/af0b0652-d0ae-4eed-867f-167f9d970db0/status",
    "cancel_url": "https://queue.fal.run/VISIONREIMAGINE/d11f80a6-1d26-452b-bdf2-14eacd823871/requests/af0b0652-d0ae-4eed-867f-167f9d970db0/cancel",
    "logs": null,
    "metrics": {},
    "queue_position": 0
}```
You can use the status_url with the same headers to check the status and then once you get the completed status you can use the response_url to see your response. You should get the response in this format
```json
{
    "status": "success",
    "images": [
        {
            "filename": "ComfyUI_00002_.png",
            "image": {
                "url": "https://fal.media/files/koala/FepkJXVcW306v7fF5alrA_6750ac9ada0e4b4a9a87b01536e594cc.png",
                "content_type": "image/png",
                "file_name": "6750ac9ada0e4b4a9a87b01536e594cc.png",
                "file_size": 2185448,
                "width": null,
                "height": null
            }
        }
    ]
}

```

