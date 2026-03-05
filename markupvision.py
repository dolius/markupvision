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
# Change the Settings to target the html you want to IMAGE up
# -----------------------------
HTML_FILE = "demo.html"
IMG_DIR = "img"
IMAGE_SIZE = "1024x1024"

os.makedirs(IMG_DIR, exist_ok=True)

# -----------------------------
# Load HTML
# -----------------------------
with open(HTML_FILE, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

images = soup.find_all("img", attrs={"data-prompt": True})

if not images:
    print("No AI images found.")
    exit()

# -----------------------------
# Process images
# -----------------------------
for img in images:

    prompt = img["data-prompt"]

    # create semantic filename
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

    # update HTML
    img["src"] = f"{IMG_DIR}/{filename}"
    del img["data-prompt"]

# -----------------------------
# Save updated HTML
# -----------------------------
with open(HTML_FILE, "w", encoding="utf-8") as f:
    f.write(str(soup))

print("\n✅ HTML updated successfully.")