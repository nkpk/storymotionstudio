import os
import requests

HF_TOKEN = os.environ.get("HF_TOKEN")
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"

def generate_image(prompt: str, output_path: str, style: str = ""):
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}

    style_prompts = {
        "Horror Cinematic": "dark, horror, cinematic lighting, eerie atmosphere, ",
        "Anime Recap": "anime style, vibrant colors, detailed illustration, ",
        "Documentary": "realistic, documentary photography, natural lighting, ",
        "Science Explainer": "clean, modern, scientific illustration, bright, ",
        "Luxury Storytelling": "luxurious, elegant, warm tones, cinematic, ",
        "Viral Shorts": "vibrant, bold, eye-catching, high contrast, ",
    }

    full_prompt = style_prompts.get(style, "") + prompt

    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json={"inputs": full_prompt},
            timeout=8
        )
        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            return output_path
        else:
            return None
    except Exception as e:
        print(f"HF skipped: {e}")
        return None