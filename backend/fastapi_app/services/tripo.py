import asyncio
from tripo3d import TripoClient, TaskStatus
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("TRIPO_API_KEY")


async def main():
    try:
        async with TripoClient(api_key=API_KEY) as client:
            task_id = await client.text_to_model(
                prompt="a small cat",
                negative_prompt="low quality, blurry",
            )
            print(f"Task ID: {task_id}")

            task = await client.wait_for_task(task_id, verbose=True)
            
            # Create output directory if it doesn't exist
            os.makedirs("./output", exist_ok=True)
            
            if task.status == TaskStatus.SUCCESS:
                files = await client.download_task_models(task, "./output")
                for model_type, path in files.items():
                    print(f"Downloaded {model_type}: {path}")
            else:
                print(f"Task failed with status: {task.status}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())