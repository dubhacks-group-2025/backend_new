import asyncio
from tripo3d import TripoClient, TaskStatus
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("TRIPO_API_KEY")
TEST_URL = "https://farm9.staticflickr.com/8505/8441256181_4e98d8bff5_z_d.jpg'"  # Replace with a valid image URL

async def main(image_url: str = TEST_URL):
    try:
        async with TripoClient(api_key=API_KEY) as client:
            # Following the exact API specification
            task_id = await client.image_to_model(
                image_url  # Direct URL to image (JPEG/PNG, max 20MB)
            )
            print(f"Task ID: {task_id}")

            # Wait for the task to complete
            task = await client.wait_for_task(task_id, verbose=True)
            
            # Create output directory if it doesn't exist
            os.makedirs("./output", exist_ok=True)

            if task.status == TaskStatus.SUCCESS:
                # Download the generated models
                files = await client.download_task_models(task, "./output")
                for model_type, path in files.items():
                    print(f"Downloaded {model_type}: {path}")
                return files
            else:
                print(f"Task failed with status: {task.status}")
                return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

if __name__ == "__main__":
    asyncio.run(main())