import os
import asyncio
from tripo3d import TripoClient, TaskStatus

# BEFORE running: export TRIPO_API_KEY='tsk_...'
API_KEY = 'tsk_V37aRysVk5g0GbTRURQr-RheEDAxK5EuWJ1C7LtZH8-'

IMAGE_PATH = "/Users/simon_pl19nc8/Desktop/School/Extracurriculars/Hackathons/DUBHACKS/dubhacks-2025/images/download-1.png"
OUTPUT_DIR = "./output"  # will be created if missing

async def main():
    if not API_KEY:
        raise RuntimeError("Set TRIPO_API_KEY in your environment.")

    # Use the context manager to auto-close the client session
    async with TripoClient(api_key=API_KEY) as client:
        # Kick off the image→model task
        task_id = await client.image_to_model(image=IMAGE_PATH)
        print(f"Task ID: {task_id}")

        # Wait for completion (prints progress if verbose=True)
        task = await client.wait_for_task(task_id, verbose=True)

        if task.status == TaskStatus.SUCCESS:
            print("✅ Task completed successfully")

            # Download resulting files (GLB/OBJ/MTL/texture(s) depending on plan)
            downloaded = await client.download_task_models(task, OUTPUT_DIR)

            for model_type, file_path in downloaded.items():
                if file_path:
                    print(f"Downloaded {model_type}: {file_path}")
        else:
            # You can inspect task.error for details
            print(f"❌ Task failed: {task.error}")

if __name__ == "__main__":
    asyncio.run(main())
