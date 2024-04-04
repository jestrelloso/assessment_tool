import os
from fastapi import UploadFile


async def save_image(image: UploadFile):
    try:
        os.makedirs("images", exist_ok=True)  # Ensure the directory exists
        image_path = os.path.join("images", image.filename)
        with open(image_path, "wb") as buffer:
            content = await image.read()  # async read
            buffer.write(content)
        return image_path
    except Exception as e:
        print(f"An error occurred while saving the image: {e}")
        return None
