import os
import sys
import argparse
import time

# Ensure project root is on the path so utils can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ollama_client import OllamaClient
from visualization_brain import VisualizationBrain
from narration_engine import NarrationEngine
from whiteboard_renderer import WhiteboardRenderer
from video_composer import VideoComposer
from utils.language_detect import detect_language

def main():
    parser = argparse.ArgumentParser(description="AI-Assisted Code Explanation and Whiteboard Visualization System")
    parser.add_argument("input_file", help="Path to the input source code file")
    parser.add_argument("--output", default="output/final_video.mp4", help="Path to output video file")
    parser.add_argument("--resolution", default="720p", choices=["720p", "1080p"], help="Output resolution (default: 720p)")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode (single scene, fast)")
    args = parser.parse_args()

    if not os.path.exists(args.input_file):
        print(f"Error: File '{args.input_file}' not found.")
        return

    # 1. Read Code
    print(f"--- Step 1: Reading Code from {args.input_file} ---")
    with open(args.input_file, 'r') as f:
        code_content = f.read()

    # 1.5 Detect Language
    language = detect_language(file_path=args.input_file, code=code_content)
    print(f"Detected language: {language}")

    # 2. Explain Code
    brain = VisualizationBrain()
    print("--- Step 2: Generating Explanation ---")
    explanation = brain.generate_explanation(code_content, language=language)
    if not explanation:
        print("Failed to generate explanation.")
        return
    print("Explanation generated.")

    # 3. Plan Visualization
    print("--- Step 3: Planning Visualization ---")
    plan = brain.generate_visualization_plan(code_content, explanation, language=language)
    if not plan or 'scenes' not in plan:
        print("Failed to generate visualization plan or invalid format.")
        if plan: print(plan)
        return
    
    scenes = plan['scenes']
    print(f"Generated {len(scenes)} scenes.")

    # 4. Output Validation (PRD 10.2, 10.5)
    print("--- Step 4: Output Validation ---")
    if not scenes:
        print("\n[VITAL ERROR] No scenes were generated. Aborting pipeline.")
        print("Check VisualizationBrain logs or Ollama status.")
        return

    for i, scene in enumerate(scenes):
        if not scene.get('narration_text'):
            print(f"\n[VITAL ERROR] Scene {i+1} is missing mandatory 'narration_text'.")
            print("Aborting pipeline to prevent incomplete video generation.")
            return
        if not scene.get('actions'):
            print(f"\n[WARNING] Scene {i+1} has no actions. It will be a static transition.")

    if args.debug:
        print("[DEBUG] Debug mode enabled. Processing only the first scene.")
        scenes = scenes[:1]

    # 5. Generate Audio & Video Content
    print("--- Step 5: Generating Assets ---")
    narrator = NarrationEngine()
    
    # Resolution setting
    res_map = {
        "720p": (1280, 720),
        "1080p": (1920, 1080)
    }
    width, height = res_map.get(args.resolution, (1280, 720))
    renderer = WhiteboardRenderer(width=width, height=height)
    
    audio_paths = []
    video_clips = []
    
    output_audio_dir = "output/audio_cache"
    
    for i, scene in enumerate(scenes):
        print(f"Processing Scene {i+1}/{len(scenes)}...")
        try:
            # Audio
            text = scene.get('narration_text', 'Step ' + str(i))
            print(f"[Pipeline] Generating audio for scene {i}: {text[:50]}...")
            audio_path = narrator.generate_audio(text, output_audio_dir)
            if not audio_path:
                print(f"[Pipeline] Warning: Failed audio for scene {i+1}")
                # Fallback? continue or insert silent placeholder logic?
                # For now continue, will break composer loop early
                continue
            
            print(f"[Pipeline] Audio generated at: {audio_path}")
            audio_paths.append(audio_path)
            
            # Video
            # Duration will be adjusted by composer, but initial render needs nominal dur
            clip = renderer.render_scene(scene, duration=2) 
            video_clips.append(clip)
            
        except Exception as e:
            print(f"Error processing scene {i+1}: {e}")
            if args.debug: raise e

    # 6. Compose Video
    if video_clips:
        print("--- Step 6: Composing Final Video ---")
        composer = VideoComposer()
        composer.compose_video(scenes, audio_paths, video_clips, args.output)
        print(f"Done! Video saved to {args.output}")
    else:
        print("No scenes generated.")

if __name__ == "__main__":
    main()
