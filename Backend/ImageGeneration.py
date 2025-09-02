import os
import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import get_key
from time import sleep

# ================= Path setup =================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # jarvis/
FRONTEND_FILE = os.path.join(BASE_DIR, "Frontend", "Files", "ImageGeneration.data")
DATA_DIR = os.path.join(BASE_DIR, "Data")

# make sure Data folder exists
os.makedirs(DATA_DIR, exist_ok=True)

# ================= Functions =================
def open_images(prompt):
    prompt = prompt.replace(" ", "_")
    files = [f"{prompt}{i}.jpg" for i in range(1, 5)]
    
    for jpg_file in files:
        image_path = os.path.join(DATA_DIR, jpg_file)
        if os.path.exists(image_path):
            try:
                img = Image.open(image_path)
                print(f"✅ Opening image: {image_path}")
                img.show()
                sleep(1)
            except IOError:
                print(f"❌ Unable to open {image_path}")
        else:
            print(f"⚠️ File not found: {image_path}")

API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {get_key('.env', 'HuggingFaceAPIKey')}"}

# Replace the API call with this more robust version
async def query(payload):
    try:
        API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"  # More reliable model
        headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}
        
        response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ API Error {response.status_code}: {response.text}")
            return None
            
        return response.content
        
    except Exception as e:
        print(f"❌ Query error: {e}")
        return None  
async def generate_images(prompt: str):
    tasks = []
    for _ in range(4):
        payload = {
            "inputs": f"{prompt}, quality=4k, ultra high details, high resolution, seed={randint(0, 1000000)}",
        }
        task = asyncio.create_task(query(payload))
        tasks.append(task)

    image_bytes_list = await asyncio.gather(*tasks)

    for i, image_bytes in enumerate(image_bytes_list):
        if image_bytes:  # only save if valid
            path = os.path.join(DATA_DIR, f"{prompt.replace(' ', '_')}{i+1}.jpg")
            with open(path, "wb") as f:
                f.write(image_bytes)
            print(f"✅ Saved: {path}")

def GenerateImages(prompt: str):
    asyncio.run(generate_images(prompt))
    open_images(prompt)

# ================= Main Loop =================
while True:
    try:
        with open(FRONTEND_FILE, "r") as f:
            Data: str = f.read().strip()
        
        if not Data:
            sleep(1)
            continue

        Prompt, Status = Data.split(",")
        
        if Status == "True":
            print("🎨 Generating Images ...")
            GenerateImages(prompt=Prompt)
            
            with open(FRONTEND_FILE, "w") as f:
                f.write("False,False")
            
            break  # remove this if you want continuous loop
        else:
            sleep(1)
    except Exception as e:
        print("⚠️ Error:", e)
        sleep(1)


