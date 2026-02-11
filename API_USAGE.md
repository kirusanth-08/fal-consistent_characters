# Consistent Character API Usage

## Minimal API Request Format

### Required Fields

```json
{
  "prompt": "Make this person on the image standing on a ground between flower plants",
  "image_url": "https://example.com/character.jpg",
  "seed": 148059131098564,
  "resolution": "square"
}
```

### Optional Fields

```json
{
  "nsfw": false
}
```

## Complete Example Request

```json
{
  "prompt": "Make this person on the image standing on a ground between flower plants",
  "image_url": "https://example.com/character.jpg",
  "seed": 148059131098564,
  "resolution": "square",
  "nsfw": false
}
```

## Field Descriptions

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `prompt` | string | ✅ Yes | - | Text prompt for image generation (controls scene, pose, etc.) |
| `image_url` | string | ✅ Yes | - | URL of the input character/person image |
| `seed` | integer | ✅ Yes | - | Random seed for reproducible generation |
| `resolution` | string | ❌ No | `"square"` | Resolution preset (see presets below) |
| `nsfw` | boolean | ❌ No | `false` | Enable NSFW mode (sets LoRA strength to 1.0 if true, 0.0 if false) |

## Fixed Workflow Parameters

These parameters are set to optimal default values and cannot be changed via API:

- **Steps**: 4 (Flux2Scheduler)
- **CFG**: 1 (CFGGuider)
- **Sampler**: euler (KSamplerSelect)
- **Batch Size**: 1
- **LoRA**: "Flux Klein - NSFW v2.safetensors"
  - Strength: 1.0 when `nsfw=true`
  - Strength: 0.0 when `nsfw=false` (default)

## cURL Example

```bash
curl -X POST https://queue.fal.run/YOUR_TEAM/your-app-id/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Key $FAL_API_KEY" \
  -d '{
    "prompt": "Make this person on the image standing on a ground between flower plants",
    "image_url": "https://example.com/character.jpg",
    "seed": 148059131098564,
    "resolution": "square",
    "nsfw": false
  }'
```

## Python Example

```python
import fal_client

result = fal_client.submit(
    "your-username/consistent-character",
    arguments={
        "prompt": "Make this person on the image standing on a ground between flower plants",
        "image_url": "https://example.com/character.jpg",
        "seed": 148059131098564,
        "resolution": "square",
        "nsfw": False
    }
)

print(result)
```

## Response Format

```json
{
  "status": "success",
  "images": [
    {
      "url": "https://fal.media/files/.../output.png",
      "content_type": "image/png",
      "file_name": "output.png",
      "file_size": 2185448,
      "width": 1024,
      "height": 1024
    }
  ]
}
```

## Common Seeds for Testing

- `148059131098564` - Default seed from workflow
- `42` - Simple reproducible seed
- `12345` - Another common test seed

## Resolution Quick Examples

**Square Image (Social Media)**
```json
{
  "resolution": "square"
}
```

**Portrait (3:4)**
```json
{
  "resolution": "portrait_3_4"
}
```

**Landscape (16:9 - Widescreen)**
```json
{
  "resolution": "landscape_16_9"
}
```

**HD Mobile Portrait**
```json
{
  "resolution": "hd"
}
```

## NSFW Mode

- **`nsfw: false`** (default): LoRA strength = 0.0, suitable for general content
- **`nsfw: true`**: LoRA strength = 1.0, enables NSFW content generation

⚠️ **Important**: When NSFW mode is disabled (`false`), the NSFW LoRA is effectively bypassed by setting its strength to 0.
