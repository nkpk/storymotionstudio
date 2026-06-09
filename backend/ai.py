import os
from groq import Groq
import json

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def generate_script(topic: str, style: str, duration: int = 60):
    prompt = f"""You are a YouTube script writer specializing in {style} style videos.

Create a complete video script for this topic: "{topic}"

The video should be approximately {duration} seconds long.

Respond ONLY with a JSON object in this exact format, no other text:
{{
  "title": "Video title here",
  "hook": "Opening line that grabs attention",
  "scenes": [
    {{
      "id": 1,
      "narration": "What the narrator says",
      "visual": "What should be shown on screen",
      "duration": 8,
      "asset_type": "image",
      "graphic_type": null
    }},
    {{
      "id": 2,
      "narration": "Counter showing growth",
      "visual": "Counter from 0 to 1000000",
      "duration": 4,
      "asset_type": "graphic",
      "graphic_type": "counter",
      "graphic_data": {{
        "start": 0,
        "end": 1000000,
        "prefix": "$",
        "label": "Revenue Growth"
      }}
    }}
  ],
  "outro": "Closing line",
  "style": "{style}",
  "total_duration": {duration}
}}

Rules:
- Create 6-10 scenes
- Mix image scenes with graphic scenes (counter, barchart, timeline, piechart)
- Each scene should be 4-8 seconds
- Make it engaging and educational
- graphic_type can be: counter, barchart, piechart, timeline, text, icon, progressbar, null
- For barchart graphic_data include: labels (comma separated), values (comma separated), title
- For timeline graphic_data include: events (format: year:label,year:label), title
- For piechart graphic_data include: labels, values, title
- For counter graphic_data include: start, end, prefix, suffix, label
- For progressbar graphic_data include: label, percentage
- For text graphic_data include: lines (comma separated), animation
- For icon graphic_data include: icon (key name), label
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=2000,
    )

    raw = response.choices[0].message.content.strip()

    # Clean JSON
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0].strip()
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0].strip()

    script = json.loads(raw)
    return script

def generate_narration_text(script: dict):
    full_text = script.get("hook", "") + " "
    for scene in script.get("scenes", []):
        full_text += scene.get("narration", "") + " "
    full_text += script.get("outro", "")
    return full_text.strip()