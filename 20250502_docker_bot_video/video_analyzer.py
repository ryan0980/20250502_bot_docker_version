import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types
from typing import Dict, Optional
import time

# Load environment variables
# 1) Get the absolute path of app.py
BASE_DIR = Path(__file__).resolve().parent
# 2) Assume .env is in the same directory
env_path = BASE_DIR / ".env"
print("Attempting to load .env:", env_path, "exists:", env_path.is_file())
# 3) Load with encoding and override
load_dotenv(dotenv_path=str(env_path), override=True, encoding="utf-8-sig")
print("GOOGLE_API_KEY=", os.getenv("GOOGLE_API_KEY"))

def generate_action_segments(
    video_path: str,
    api_key: str | None = None,
    model: str = "gemini-2.0-flash",
    view: str | None = None,
    prompt: str | None = None,
    max_retries: int = 5,
    retry_delay: int = 2,
) -> str:
    """
    Use Gemini to split video into detailed action segments and return text results.

    Args:
        video_path: Local video file path.
        api_key: Your Google API Key; if empty, will be loaded from .env automatically.
        model: Name of the Gemini model to call.
        view: View label, optional up/front/left/right, corresponding to different perspectives.
        prompt: Custom prompt; default format requirements are embedded based on view.
        max_retries: Maximum number of retries.
        retry_delay: Retry interval (seconds).

    Returns:
        Model's returned plain text segment list.
    """
    # If no api_key provided, try loading from .env
    if api_key is None:
        api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("Environment variable GOOGLE_API_KEY not found, please check .env file")

    # Validate and read video bytes
    if not os.path.isfile(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    with open(video_path, "rb") as f:
        video_bytes = f.read()

    # View prompt mapping
    view_prompts = {
        'up': (
            "This video is captured from an overhead camera. Provide the most detailed description possible of all movements, spatial relationships between objects, relative displacements, angle changes, and sense of speed, and note any observable changes in object state (e.g., opening, locking, deformation, tension)."
        ),
        'front': (
            "This video is captured from a front-facing camera. Provide the most detailed description possible of the action sequence, including each arm's motion trajectory, the sense of gripping force, changes in object surface characteristics, and any subtle adjustments in object orientation, angle, or position."
        ),
        'left': (
            "This video is captured by a camera mounted on the left robotic arm. From the left-arm perspective, provide a thorough description of each extension, rotation, and gripping action, focusing on any deformation, posture changes, and relative position shifts of objects upon contact, as well as changes in the left arm's joint angles."
        ),
        'right': (
            "This video is captured by a camera mounted on the right robotic arm. From the right-arm perspective, provide a thorough description of each movement, gripping action, direction and magnitude of applied force, and describe any changes in object state, including position, orientation, locking, or any physical interactions."
        ),
    }

    default_prompt = "Split the video into the finest-grained action segments, each focusing on one distinct action, and include the following details:\n" + \
        "1. Time range (MM:SS–MM:SS)\n" + \
        "2. Actor (left arm, right arm, or both)\n" + \
        "3. Target object and any relevant properties (material, shape, etc.)\n" + \
        "4. Motion trajectory, sense of speed, and direction of force\n" + \
        "5. Any changes in object state or position (e.g., locked, released, rotated, displaced)\n\n" + \
        "6. Output ONLY the unified list, one segment per line, with no extra text.\n\n" + \
        "Example:\n" + \
        "00:00–00:03 : The left robotic arm moves along a straight trajectory toward the center, grasps the translucent plastic container with slight locking pressure.\n" + \
        "00:03–00:06 : The right robotic arm rotates clockwise by 45° at a slow pace, pushing a Duracell battery into the compartment until an audible click.\n" + \
        "00:06–00:09 : Both arms lift upward and retract in synchronization, leaving the closed battery compartment behind."

    # Assemble the final prompt
    if prompt is None:
        prompt = ""
        if view in view_prompts:
            prompt += view_prompts[view] + "\n\n"
        prompt += default_prompt


    # Call Gemini, with retry mechanism
    client = genai.Client(api_key=api_key)
    content = types.Content(parts=[
        types.Part(inline_data=types.Blob(data=video_bytes, mime_type="video/mp4")),
        types.Part(text=prompt),
    ])
    
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(model=model, contents=content)
            return response.text
        except Exception as e:
            error_str = str(e)
            if ("503" in error_str or "500" in error_str) and attempt < max_retries - 1:
                print(f"Encountered error ({error_str}), waiting {retry_delay} seconds before retrying... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(retry_delay)
            else:
                raise e

def analyze_all_videos(video_paths: Dict[str, str], api_key: Optional[str] = None) -> Dict[str, str]:
    """
    Analyze videos from all perspectives
    
    Args:
        video_paths: Dictionary containing paths of videos from four perspectives
        api_key: Google API Key
        
    Returns:
        Dictionary containing analysis results for each perspective
    """
    results = {}
    view_mapping = {
        'top': 'up',
        'front': 'front',
        'left': 'left',
        'right': 'right'
    }
    
    for view, path in video_paths.items():
        try:
            print(f"\nAnalyzing {view} perspective video:")
            print(f"Video path: {path}")
            print(f"Perspective label: {view_mapping[view]}")
            
            segments = generate_action_segments(
                video_path=path,
                api_key=api_key,
                view=view_mapping[view]
            )
            results[view] = segments
            
            print(f"Analysis results:\n{segments}")
            print("-" * 50)
        except Exception as e:
            error_msg = f"Analysis failed: {str(e)}"
            print(f"Analysis failed: {error_msg}")
            results[view] = error_msg
            
    return results 