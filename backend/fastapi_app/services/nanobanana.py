import os
from io import BytesIO
from PIL import Image
import requests

from google import genai  # pip install google-genai
from google.genai import types
import firebase_admin
from firebase_admin import credentials, storage, firestore

from datetime import timedelta
from fastapi import APIRouter, HTTPException

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# --- SDK Initialization (do this once in your application) ---
# Make sure to replace 'path/to/your/serviceAccountKey.json' with your actual key file.
# You can download this from your Firebase Project Settings -> Service Accounts tab.
cred = credentials.Certificate('/Users/simon_pl19nc8/Desktop/School/Extracurriculars/Hackathons/DUBHACKS/dubhacks-2025/backend/fastapi_app/services/dubhacks2025-26629-firebase-adminsdk-fbsvc-307e4954c1.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': 'dubhacks2025-26629.appspot.com' # Your project's default storage bucket
})

db = firestore.client()

def get_image_from_firebase_storage(image_path: str) -> Image.Image:
    """Download image from Firebase Storage using Admin SDK."""
    bucket = storage.bucket()
    blob = bucket.blob(image_path)
    
    # Download the image content as bytes
    image_data = blob.download_as_bytes()
    
    # Convert to PIL Image
    return Image.open(BytesIO(image_data))

def url_to_image(url: str) -> Image.Image:
    """Download image from URL and return PIL Image object."""
    # Add https:// if the URL doesn't have a scheme
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    response = requests.get(url)
    response.raise_for_status()
    return Image.open(BytesIO(response.content))

def get_item_from_firestore(collection_name: str='drawings', document_id: str='2iYllCFtF5yQqWMOaHRs', attribute_name: str='OriginalImageUrl') -> str:
    
    doc_ref = db.collection(collection_name).document(document_id)
    doc = doc_ref.get()

    if doc.exists:
        data = doc.to_dict()
        
        if attribute_name in data:
            attribute_value = data[attribute_name]
            print(f"The value of '{attribute_name}' is: {attribute_value}")
            return attribute_value
        else:
            print(f"Attribute '{attribute_name}' not found in document.")
    else:
        print(f"No such document: {document_id}")


def generate_image(prompt: str, out_path: str) -> list[Image.Image]:
    # Get the image directly from Firebase Storage using the file path
    # Assuming the image is stored as 'Profile_Photo_Tennis.JPG' in your storage
    image = get_image_from_firebase_storage('Profile_Photo_Tennis.JPG')
    image.save("nanobanana_sample.png")

    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[prompt, image],
    )

    for part in response.candidates[0].content.parts:
        if part.text is not None:
            print(part.text)
        elif part.inline_data is not None:
            image = Image.open(BytesIO(part.inline_data.data))
            image.save("generated_image.png")



if __name__ == "__main__":
    # Example usage
    example_prompt = (
        "A cartoon character playing tennis "
        "with a ping pong paddle and a tennis ball"
    )

    
    
    generate_image(example_prompt, out_path="nanobanana_sample.png")
    #generate_image(example_prompt, out_path="nanobanana_sample.png")
    
    print(get_item_from_firestore(attribute_name='OriginalImageUrl'))
