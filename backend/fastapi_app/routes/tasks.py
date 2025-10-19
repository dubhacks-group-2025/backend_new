from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict
from io import BytesIO
import sys
import os
import uuid
from pathlib import Path

# Add the parent directory to the path to import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.nanobanana import generate_images
from fastapi.responses import JSONResponse

router = APIRouter()

class GenerateImageRequest(BaseModel):
    prompt: str
    reference_url: Optional[HttpUrl] = None

@router.post("/generate_image")
async def generate_image_endpoint(request: GenerateImageRequest) -> Dict[str, str]:
    """
    Generate an image using Google's Imagen model.
    
    Args:
        request: JSON body with prompt and optional reference_url
    
    Returns:
        Dictionary containing either a URL to the generated image or a base64 data URI
    """
    try:
        # Convert HttpUrl to string if provided
        reference_url = str(request.reference_url) if request.reference_url else None
        
        # Generate the image using the nanobanana service
        result = await generate_images(request.prompt, reference_url)
        
        if not result['generated_image']:
            raise HTTPException(status_code=500, detail="Failed to generate image")
        
        generated_image = result['generated_image']
        
        # Create images directory if it doesn't exist
        images_dir = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) / 'images'
        images_dir.mkdir(exist_ok=True)
        
        # Generate a unique filename
        filename = f"generated-image-{uuid.uuid4()}.png"
        image_path = images_dir / filename
        
        # Save the image
        generated_image.save(image_path, format='PNG')
        
        # Return the URL to the saved image
        image_url = f"/images/{filename}"
        return JSONResponse({
            "url": image_url,
            "message": "Image generated and saved successfully"
        })
        
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating image: {str(e)}")
