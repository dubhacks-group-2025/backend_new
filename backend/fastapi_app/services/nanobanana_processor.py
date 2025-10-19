"""
Firebase Cloud Function to process uploaded images and generate nanobanana versions.
This function is triggered when a new image is uploaded to Firebase Storage.
"""

import os
import sys
from firebase_functions import https_fn, storage_fn
from firebase_admin import initialize_app, firestore, storage
import firebase_admin

# Add the services directory to the path so we can import nanobanana
sys.path.append(os.path.join(os.path.dirname(__file__), '../../backend/fastapi_app/services'))

from nanobanana import process_uploaded_image

# Initialize Firebase Admin SDK
initialize_app()

@storage_fn.on_object_finalized()
def process_uploaded_image_trigger(event: storage_fn.CloudEvent[storage_fn.StorageObjectData]):
    """
    Cloud Function triggered when a new image is uploaded to Firebase Storage.
    This function processes the uploaded image and generates a nanobanana version.
    """
    try:
        # Get the uploaded file information
        file_name = event.data.name
        bucket_name = event.data.bucket
        
        print(f"Processing uploaded file: {file_name} from bucket: {bucket_name}")
        
        # Skip if it's already a generated image or not an image file
        if file_name.startswith('generated_images/') or not file_name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
            print(f"Skipping file: {file_name}")
            return
        
        # Construct the public URL for the uploaded image
        image_url = f"https://storage.googleapis.com/{bucket_name}/{file_name}"
        
        # For now, use a default prompt - you can modify this to get the prompt from Firestore
        # or from the file metadata
        prompt = "Transform this image into a cartoon nanobanana character while keeping the main subject recognizable"
        
        # Extract user ID from file path if it follows a pattern like 'users/{userId}/images/{filename}'
        user_id = None
        if 'users/' in file_name:
            try:
                user_id = file_name.split('/')[1]  # Extract user ID from path
            except:
                pass
        
        # Process the image
        result = process_uploaded_image(
            original_image_url=image_url,
            prompt=prompt,
            user_id=user_id
        )
        
        if result['success']:
            print(f"Successfully processed image. Generated image URL: {result['generatedImageUrl']}")
            print(f"Document ID: {result['documentId']}")
        else:
            print(f"Failed to process image: {result['error']}")
            
    except Exception as e:
        print(f"Error in process_uploaded_image_trigger: {e}")
        raise e

@https_fn.on_request()
def process_image_manual(req: https_fn.Request) -> https_fn.Response:
    """
    Manual HTTP trigger to process an image with a custom prompt.
    POST request body should contain:
    {
        "imageUrl": "https://...",
        "prompt": "your prompt here",
        "userId": "optional_user_id"
    }
    """
    try:
        # Handle CORS
        if req.method == 'OPTIONS':
            headers = {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
            }
            return https_fn.Response('', 204, headers)
        
        if req.method != 'POST':
            return https_fn.Response('Method not allowed', 405)
        
        # Parse request data
        data = req.get_json()
        if not data:
            return https_fn.Response('No JSON data provided', 400)
        
        image_url = data.get('imageUrl')
        prompt = data.get('prompt')
        user_id = data.get('userId')
        
        if not image_url or not prompt:
            return https_fn.Response('imageUrl and prompt are required', 400)
        
        # Process the image
        result = process_uploaded_image(
            original_image_url=image_url,
            prompt=prompt,
            user_id=user_id
        )
        
        # Return result with CORS headers
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json',
        }
        
        return https_fn.Response(str(result), 200, headers)
        
    except Exception as e:
        print(f"Error in process_image_manual: {e}")
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json',
        }
        return https_fn.Response(f'{{"error": "{str(e)}"}}', 500, headers)
