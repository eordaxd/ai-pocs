import os
import base64
import io
import requests
from flask import Flask, render_template, request, jsonify
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10MB max upload

API_KEY = os.getenv("NANOBANANA_API_KEY")
API_URL = "https://api.nanobanana.ai/v1/inpaint"  # placeholder — update if different

INPAINT_PROMPT = (
    "Remove all people and persons from this image completely. "
    "Replace the areas where people were with natural, realistic background "
    "that seamlessly matches the surrounding environment, maintaining consistent "
    "lighting, perspective, texture, and color. The result should look like the "
    "people were never there."
)
NEGATIVE_PROMPT = (
    "people, person, human, man, woman, child, body, face, hands, feet, "
    "shadow of person, distorted, blurry, artifacts, unrealistic"
)


def encode_image(pil_image: Image.Image) -> str:
    buf = io.BytesIO()
    pil_image.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def call_inpaint_api(image_b64: str, mask_b64: str) -> str:
    """Call the NanoBanana inpainting API and return the result image as base64."""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "image": image_b64,
        "mask": mask_b64,
        "prompt": INPAINT_PROMPT,
        "negative_prompt": NEGATIVE_PROMPT,
        "num_inference_steps": 50,
        "guidance_scale": 7.5,
    }
    resp = requests.post(API_URL, json=payload, headers=headers, timeout=120)
    resp.raise_for_status()
    data = resp.json()

    # Adapt to API response shape — common patterns:
    if "image" in data:
        return data["image"]
    if "output" in data:
        output = data["output"]
        if isinstance(output, list):
            return output[0]
        return output
    raise ValueError(f"Unexpected API response: {data}")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/remove-people", methods=["POST"])
def remove_people():
    if not API_KEY:
        return jsonify({"error": "NANOBANANA_API_KEY not set in environment"}), 500

    data = request.get_json()
    if not data or "image" not in data or "mask" not in data:
        return jsonify({"error": "Missing image or mask"}), 400

    try:
        # Decode and validate the uploaded image
        image_data = base64.b64decode(data["image"].split(",")[-1])
        mask_data = base64.b64decode(data["mask"].split(",")[-1])

        image = Image.open(io.BytesIO(image_data)).convert("RGB")
        mask = Image.open(io.BytesIO(mask_data)).convert("L")

        # Resize mask to match image if needed
        if mask.size != image.size:
            mask = mask.resize(image.size, Image.LANCZOS)

        image_b64 = encode_image(image)
        mask_b64 = encode_image(mask)

        result_b64 = call_inpaint_api(image_b64, mask_b64)
        return jsonify({"result": f"data:image/png;base64,{result_b64}"})

    except requests.HTTPError as e:
        return jsonify({"error": f"API error: {e.response.status_code} — {e.response.text}"}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5050)
