import os
import base64
from slugify import slugify
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai import OpenAI

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise Exception("OPENAI_API_KEY not found in .env file")

client = OpenAI(api_key=api_key)

# -----------------------------
# Resolve project root
# -----------------------------
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# -----------------------------
# Image settings
# -----------------------------
IMG_DIR = os.path.join(ROOT, "img")
IMAGE_SIZE = "1024x1024"

os.makedirs(IMG_DIR, exist_ok=True)

# -----------------------------
# TARGET HTML FILES - target sibligns of this script or adjust paths as needed
# -----------------------------
TARGET_HTML_FILES = [

    "uipeek/index.html",
    "other/about.html",

]

# -----------------------------
# Process HTML files
# -----------------------------
for target in TARGET_HTML_FILES:

    html_path = os.path.join(ROOT, target)

    if not os.path.exists(html_path):
        print("⚠ File not found:", target)
        continue

    print("\n📄 Processing:", target)

    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    images = soup.find_all("img", attrs={"data-prompt": True})

    if not images:
        print("No AI images found.")
        continue

    # -----------------------------
    # Process images
    # -----------------------------
    for img in images:

        prompt = img["data-prompt"]

        filename = slugify(prompt)[:60] + ".png"
        filepath = os.path.join(IMG_DIR, filename)

        if os.path.exists(filepath):
            print("✔ Using existing image:", filename)

        else:
            print("🎨 Generating image:", prompt)

            result = client.images.generate(
                model="gpt-image-1",
                prompt=prompt,
                size=IMAGE_SIZE
            )

            image_base64 = result.data[0].b64_json
            image_bytes = base64.b64decode(image_base64)

            with open(filepath, "wb") as f:
                f.write(image_bytes)

            print("✓ Saved:", filename)

        # relative path so HTML works
        rel_path = os.path.relpath(filepath, os.path.dirname(html_path))
        img["src"] = rel_path.replace("\\", "/")

        del img["data-prompt"]

    # -----------------------------
    # Save updated HTML
    # -----------------------------
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(str(soup))

    print("✅ HTML updated:", target)

print("\n🚀 All pages processed.")