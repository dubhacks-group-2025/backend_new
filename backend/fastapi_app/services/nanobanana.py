from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import aiohttp
import asyncio
from typing import Union, List, Optional

client = genai.Client()

async def download_image_from_url(session: aiohttp.ClientSession, url: str) -> Optional[Image.Image]:
    """Download an image from a URL asynchronously."""
    try:
        async with session.get(url) as response:
            if response.status == 200:
                image_data = await response.read()
                return Image.open(BytesIO(image_data))
            else:
                print(f"Failed to download image from {url}: Status {response.status}")
                return None
    except Exception as e:
        print(f"Error downloading image from {url}: {e}")
        return None

async def generate_images(
    prompt: str, 
    reference_url: Optional[str] = None
):
    
    result = {
        'generated_image': None,
        'reference_image': None
    }
    
    # Download reference image if URL is provided
    if reference_url:
        async with aiohttp.ClientSession() as session:
            reference_image = await download_image_from_url(session, reference_url)
            result['reference_image'] = reference_image
    
    # Generate single image using the prompt
    response = client.models.generate_images(
        model='imagen-4.0-generate-001',
        prompt=prompt,
        config=types.GenerateImagesConfig(
            number_of_images=1,
        )
    )
    
    # Get the single generated image
    if response.generated_images:
        result['generated_image'] = response.generated_images[0].image
        # Uncomment the line below if you want to display the image
        # response.generated_images[0].image.show()
    
    return result