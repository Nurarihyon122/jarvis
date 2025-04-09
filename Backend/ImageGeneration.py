import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import get_key
import os
from time import sleep

# ✅ Ensure the image folder exists
os.makedirs("Data", exist_ok=True)

# ✅ Hugging Face API config
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {get_key('.env', 'HuggingFaceAPIKey')}"}

# ✅ Log that the script is running
print("[🟢] ImageGeneration.py running and watching for prompts...")

# ✅ Function to display images
def open_images(prompt):
    safe_prompt = prompt.replace(" ", "_")
    files = [f"{safe_prompt}_{i}.jpg" for i in range(1, 5)]
    for file in files:
        path = os.path.join("Data", file)
        if os.path.exists(path):
            print(f"[🖼️] Opening image: {path}")
            os.startfile(path)  # Windows only
        else:
            print(f"[❌] File not found: {path}")

# ✅ Send image generation request to API
async def query(payload):
    response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
    print(f"[🌐] API Status: {response.status_code}")
    if response.status_code != 200:
        print(f"[❌] API Error: {response.content}")
    return response.content

# ✅ Generate and save images
async def generate_images(prompt: str):
    tasks = []
    for _ in range(4):
        payload = {
            "inputs": f"{prompt}, quality=4K, sharpness=maximum, Ultra High details, high resolution, seed={randint(0, 1000000)}"
        }
        tasks.append(asyncio.create_task(query(payload)))

    image_bytes_list = await asyncio.gather(*tasks)

    for i, image_bytes in enumerate(image_bytes_list):
        filename = f"Data/{prompt.replace(' ', '_')}_{i + 1}.jpg"
        with open(filename, "wb") as f:
            f.write(image_bytes)
            print(f"[✅] Image saved: {filename}")

# ✅ Wrapper
def GenerateImages(prompt: str):
    asyncio.run(generate_images(prompt))
    open_images(prompt)

# ✅ Main loop
while True:
    try:
        print("[🔁] Checking for image generation requests...")
        with open(r"Frontend\Files\ImageGeneration.data", "r") as f:
            data = f.read()

        Prompt, Status = data.strip().split(",")

        if Status == "True":
            print(f"[🚀] Generating images for: {Prompt}")
            GenerateImages(Prompt)

            with open(r"Frontend\Files\ImageGeneration.data", "w") as f:
                f.write("False,False")

            print("[✅] Image generation done. Awaiting next request...")

        sleep(1)

    except Exception as e:
        print(f"[❌] Error: {e}")
        sleep(1)
