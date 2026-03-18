# PoC: People Remover

## What

A web tool that removes people from photos using AI inpainting. The user uploads an image, paints over the people they want removed, and the app calls the NanoBanana inpainting API to fill those regions with realistic background.

## Why

Validates whether NanoBanana's inpainting API can produce convincing people-removal results via a simple brush-based UI, without requiring any manual segmentation tooling.

## Architecture

```
src/
├── main.py               # Flask backend — handles upload, mask prep, API call
├── templates/
│   └── index.html        # Single-page UI
└── static/
    ├── style.css
    └── app.js            # Canvas painting, mask generation, API wiring
```

**Flow:**
1. User uploads image → resized client-side to ≤ 1024px
2. User paints red mask over people
3. Browser converts mask to binary (white = inpaint, black = keep)
4. Flask encodes image + mask as base64, sends to NanoBanana API with inpainting prompt
5. Result image returned and displayed alongside original

**Inpainting prompt used:**
> Remove all people and persons from this image completely. Replace the areas where people were with natural, realistic background that seamlessly matches the surrounding environment, maintaining consistent lighting, perspective, texture, and color. The result should look like the people were never there.

## How to Run

```bash
cd ai-pocs/pocs/people-remover
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your NANOBANANA_API_KEY
python src/main.py
# open http://localhost:5050
```

## Results / Findings

<!-- Fill in after testing -->

## Next Steps

- [ ] Add auto-detection of people via a segmentation model (e.g. SAM) to auto-generate the mask
- [ ] Support batch processing
- [ ] Tune prompt / guidance scale based on API results
