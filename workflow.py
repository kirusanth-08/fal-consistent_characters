WORKFLOW_JSON={
  "input": {
    "uid": "testUid",
    "customNodes": [],
    "customModels": [],
    "images": [],
    "workflow": {
      "99": {
        "inputs": {
          "noise": [
            "109",
            0
          ],
          "guider": [
            "110",
            0
          ],
          "sampler": [
            "111",
            0
          ],
          "sigmas": [
            "103",
            0
          ],
          "latent_image": [
            "102",
            0
          ]
        },
        "class_type": "SamplerCustomAdvanced",
        "_meta": {
          "title": "SamplerCustomAdvanced"
        }
      },
      "100": {
        "inputs": {
          "clip_name": "qwen_3_8b_fp8mixed.safetensors",
          "type": "flux2",
          "device": "default"
        },
        "class_type": "CLIPLoader",
        "_meta": {
          "title": "Load CLIP"
        }
      },
      "101": {
        "inputs": {
          "vae_name": "flux2-vae.safetensors"
        },
        "class_type": "VAELoader",
        "_meta": {
          "title": "Load VAE"
        }
      },
      "102": {
        "inputs": {
          "width": 3072,
          "height": 3072,
          "batch_size": 1
        },
        "class_type": "EmptyFlux2LatentImage",
        "_meta": {
          "title": "Empty Flux 2 Latent"
        }
      },
      "103": {
        "inputs": {
          "steps": 4,
          "width": [
            "117",
            0
          ],
          "height": [
            "117",
            1
          ]
        },
        "class_type": "Flux2Scheduler",
        "_meta": {
          "title": "Flux2Scheduler"
        }
      },
      "104": {
        "inputs": {
          "upscale_method": "nearest-exact",
          "megapixels": 1,
          "resolution_steps": 1,
          "image": [
            "125",
            0
          ]
        },
        "class_type": "ImageScaleToTotalPixels",
        "_meta": {
          "title": "ImageScaleToTotalPixels"
        }
      },
      "105": {
        "inputs": {
          "pixels": [
            "104",
            0
          ],
          "vae": [
            "101",
            0
          ]
        },
        "class_type": "VAEEncode",
        "_meta": {
          "title": "VAE Encode"
        }
      },
      "106": {
        "inputs": {
          "samples": [
            "99",
            0
          ],
          "vae": [
            "101",
            0
          ]
        },
        "class_type": "VAEDecode",
        "_meta": {
          "title": "VAE Decode"
        }
      },
      "107": {
        "inputs": {
          "conditioning": [
            "119",
            0
          ],
          "latent": [
            "105",
            0
          ]
        },
        "class_type": "ReferenceLatent",
        "_meta": {
          "title": "ReferenceLatent"
        }
      },
      "108": {
        "inputs": {
          "conditioning": [
            "115",
            0
          ],
          "latent": [
            "105",
            0
          ]
        },
        "class_type": "ReferenceLatent",
        "_meta": {
          "title": "ReferenceLatent"
        }
      },
      "109": {
        "inputs": {
          "noise_seed": 148059131098564
        },
        "class_type": "RandomNoise",
        "_meta": {
          "title": "RandomNoise"
        }
      },
      "110": {
        "inputs": {
          "cfg": 1,
          "model": [
            "116",
            0
          ],
          "positive": [
            "107",
            0
          ],
          "negative": [
            "108",
            0
          ]
        },
        "class_type": "CFGGuider",
        "_meta": {
          "title": "CFGGuider"
        }
      },
      "111": {
        "inputs": {
          "sampler_name": "euler"
        },
        "class_type": "KSamplerSelect",
        "_meta": {
          "title": "KSamplerSelect"
        }
      },
      "113": {
        "inputs": {
          "unet_name": "flux-2-klein-9b.safetensors",
          "weight_dtype": "default"
        },
        "class_type": "UNETLoader",
        "_meta": {
          "title": "Load Diffusion Model"
        }
      },
      "115": {
        "inputs": {
          "conditioning": [
            "119",
            0
          ]
        },
        "class_type": "ConditioningZeroOut",
        "_meta": {
          "title": "ConditioningZeroOut"
        }
      },
      "116": {
        "inputs": {
          "lora_name": "Flux Klein - NSFW v2.safetensors",
          "strength_model": 0.0,
          "model": [
            "113",
            0
          ]
        },
        "class_type": "LoraLoaderModelOnly",
        "_meta": {
          "title": "Load LoRA"
        }
      },
      "117": {
        "inputs": {
          "image": [
            "104",
            0
          ]
        },
        "class_type": "GetImageSize",
        "_meta": {
          "title": "Get Image Size"
        }
      },
      "119": {
        "inputs": {
          "text": "Make this person on the image standing on a ground between flower plants ",
          "clip": [
            "100",
            0
          ]
        },
        "class_type": "CLIPTextEncode",
        "_meta": {
          "title": "CLIP Text Encode (Positive Prompt)"
        }
      },
      "121": {
        "inputs": {
          "filename_prefix": "output",
          "images": [
            "106",
            0
          ]
        },
        "class_type": "SaveImage",
        "_meta": {
          "title": "Save Image"
        }
      },
      "125": {
        "inputs": {
          "image": "input_image.png"
        },
        "class_type": "LoadImage",
        "_meta": {
          "title": "Load Image"
        }
      }
    }
  }
}