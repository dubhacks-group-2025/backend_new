import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("TRIPO_API_KEY")
BASE_URL = "https://api.tripo3d.ai/v2/openapi/task"

def convert_glb_to_usdz(original_model_task_id):
    """
    Convert a GLB model to USDZ format using the conversion API.
    
    Args:
        original_model_task_id (str): The task_id from a previous model generation task
        
    Returns:
        str: The URL of the usdz version of the model
    """
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "type": "convert_model",
        "format": "USDZ",
        "original_model_task_id": original_model_task_id
    }
    
    try:
        response = requests.post(BASE_URL, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()

        # Print full response for debugging
        print(f"Full API Response: {result}")
        
        task_id = result['data']['task_id']

        # get URL from task id - replace :task_id with actual task_id
        get_response = requests.get(f"{BASE_URL}/{task_id}", headers=headers)
        res = get_response.json()
        
        print(f"Task status response: {res}")  # Debug print
        
        if 'output' in res and 'model' in res['output']:
            return res['output']['model']
        else:
            print("Warning: No model URL found in response")
            return None
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Error during conversion: {e}")
        raise

# Example usage
if __name__ == "__main__":
    id = "cd9ca7de-9c88-49cb-a7b3-b716ff1481a5"
    model_url = convert_glb_to_usdz(id)  
    print(f"New Model: {model_url}")