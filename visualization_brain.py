import json
from ollama_client import OllamaClient

class VisualizationBrain:
    def __init__(self):
        self.ollama = OllamaClient()

    def generate_explanation(self, code, language="Python"):
        """Generates a text explanation of the code."""
        prompt = f"""
        You are an expert Computer Science professor and technical educator.

        TASK:
        Analyze the given {language} code and generate a clear, step-by-step explanation that can be spoken as a narration for an educational video.

        IMPORTANT RULES:
        - Output ONLY plain text.
        - DO NOT output JSON.
        - DO NOT use code blocks.
        - DO NOT include scene descriptions or visual instructions.
        - DO NOT include timestamps.
        - DO NOT include bullet points or numbering symbols.
        - Write in natural spoken English suitable for text-to-speech.

        STYLE REQUIREMENTS:
        - Explain as if teaching a beginner student, but provide deep algorithmic INTUITION.
        - Start by clearly stating the goal and using a real-world analogy to explain WHY the approach works before diving into the code.
        - When explaining specific lines, clarify the underlying logic and your "Chain of Thought". Do not just read the syntax. Explain WHY it is happening.
        - Maintain logical flow from start to end of program execution.
        - Expand complex mathematical or vectorized operations into understandable steps.
        - For Machine Learning code, explain formulas and calculations in simple words.
        - For DSA code, explain how data structures change over time and the reasoning behind each step.
        - Mention intermediate values and what each variable represents.
        - Keep sentences short and clear for narration.
        - If the code is in a language other than Python, still explain the logic clearly.
        - Reference language-specific syntax naturally (e.g., pointers in C/C++, classes in Java).
        - CONCLUDE the explanation with a brief summary of the Time and Space Complexity.

        OUTPUT FORMAT:
        A continuous narration script divided into paragraphs.
        Each paragraph should represent a logical step of the program.

        TONE:
        Friendly, calm, teacher-like voice.

        DO NOT SAY:
        "Step 1", "Scene", "JSON", "Visualization", or any meta commentary.

        CODE:
        {code}
        """
        
        print("Generating explanation...")
        explanation = self.ollama.generate_text(prompt, system_prompt="You are an expert Computer Science professor.")
        return explanation

    def generate_visualization_plan(self, code, explanation, language="Python"):
        
        base_prompt = f"""
        You are a visualization planner for an educational whiteboard animation system.
        Your goal is to convert a step-by-step code explanation into a sequence of scenes for a whiteboard animation.
        The source code is written in {language}.

        ### AVAILABLE ACTIONS:
        You must use ONLY these action 'type's in your JSON output:

        1. SIMPLE PROGRAMS & VARIABLES:
           - {{"type": "draw_variable", "name": "var_name", "value": "val"}}
           - {{"type": "update_value", "name": "var_name", "new_value": "val"}}
           - {{"type": "print_output", "text": "string"}} : Shows text in a console panel.

        2. DATA STRUCTURES (ARRAYS):
           - {{"type": "draw_array", "name": "arr_name", "values": [1, 2, 3]}}
           - {{"type": "update_array_value", "name": "arr_name", "index": 0, "new_value": 99}}
           - {{"type": "swap_array_values", "name": "arr_name", "index1": 0, "index2": 1}}
           - {{"type": "draw_pointer", "name": "ptr_name", "target": "arr_name", "index": 0}}
           - {{"type": "move_pointer", "name": "ptr_name", "target": "arr_name", "index": 1}}

        3. HIGHLIGHTING & INSIGHTS:
           - {{"type": "highlight_variable", "name": "var_name"}}
           - {{"type": "highlight_index", "name": "arr_name", "index": 0}}
           - {{"type": "clear_highlights"}} : Resets all highlights and overlays.
           - {{"type": "show_text", "text": "Important insight"}} : Renders a persistent text overlay at the bottom of the screen. USE THIS AGGRESSIVELY to display "Think Steps", algorithmic complexity, real-world analogies, or deep insights while actions happen.

        4. RECURSION & CALL STACK:
           - {{"type": "push_stack_frame", "name": "func_name", "variables": {{"n": 3}}}}
           - {{"type": "pop_stack_frame", "return_value": 6}} : Marks the top frame for removal.
           - {{"type": "update_frame_variable", "name": "n", "value": 2}} : Updates variable in the top-most frame.

        5. MACHINE LEARNING:
           - {{"type": "draw_plot", "name": "plot_name", "plot_type": "scatter", "points": [[x,y],...], "axes": [xmin,xmax,ymin,ymax]}}
           - {{"type": "update_plot", "name": "plot_name", "line": [m, c]}} : Draws/updates y = mx + c.
           - {{"type": "update_plot", "name": "plot_name", "sigmoid": [w, b]}} : Draws/updates probability curve.
           - {{"type": "update_plot", "name": "plot_name", "residuals": true/false}}
           - {{"type": "draw_clusters", "name": "name", "points": [], "centroids": [], "assignments": [], "axes": [xmin, xmax, ymin, ymax]}}
           - {{"type": "update_clusters", "name": "name", "centroids": [], "assignments": []}} : Updates centroid positions or point assignments.

        ### PACING & THOUGHTFULNESS:
        - Your scenes must match the depth of the explanation. If the explanation introduces an analogy or complexity analysis, create a scene using "show_text" to display that thought visually!
        - Keep the viewer engaged: aggressively highlight comparing variables/indices BEFORE swapping or changing them. Explain the logic behind the change using "show_text" (e.g., "Comparing 5 > 3" or "Insight: Found smaller element").
        - Always visually represent the Time and Space complexity at the end of the animation using "show_text".

        ### OUTPUT JSON SCHEMA:
        Return a JSON array of scenes. Each scene MUST have:
        - "scene_id": integer
        - "title": A short title for the step (e.g., "Initializing Array")
        - "actions": An array of action objects (see above)
        - "narration_text": A clear, educational explanation of what is happening in this scene.

        ### EXAMPLE OUTPUT:
        [
          {{
            "scene_id": 1,
            "title": "Setup",
            "actions": [
              {{"type": "draw_array", "name": "data", "values": [10, 20, 30]}},
              {{"type": "draw_pointer", "name": "i", "target": "data", "index": 0}}
            ],
            "narration_text": "We start with an array called data and a pointer i at index 0."
          }}
        ]

        ### INPUT:
        CODE:
        {code}

        EXPLANATION:
        {explanation}

        OUTPUT ONLY THE JSON ARRAY. NO MARKDOWN. NO BRAINSTORMING.
        """
        
        system_prompt = "You are a strict JSON generator. Output only a JSON array."
        
        def extract_json_array(text):
            if not text: return None
            # Remove markdown code fences if present
            cleaned = text.replace("```json", "").replace("```", "")
            
            # Find array boundaries
            start = cleaned.find('[')
            end = cleaned.rfind(']')
            
            if start != -1 and end != -1:
                json_candidate = cleaned[start:end+1]
                try:
                    return json.loads(json_candidate)
                except json.JSONDecodeError:
                    # Try to fix common issues like trailing commas
                    import re
                    # Remove trailing comma before ] or }
                    json_candidate = re.sub(r',(\s*])', r'\1', json_candidate)
                    json_candidate = re.sub(r',(\s*})', r'\1', json_candidate)
                    return json.loads(json_candidate)
            raise ValueError("No JSON array found in response")

        def validate_and_fix_scenes(scenes):
            if not isinstance(scenes, list):
                return []
            fixed_scenes = []
            for i, scene in enumerate(scenes):
                if not isinstance(scene, dict):
                    continue
                # Ensure mandatory fields
                if "scene_id" not in scene:
                    scene["scene_id"] = i + 1
                if "title" not in scene:
                    scene["title"] = f"Scene {i+1}"
                if "actions" not in scene:
                    scene["actions"] = []
                if "narration_text" not in scene:
                    # Fallback narration if missing
                    scene["narration_text"] = f"Step {scene['scene_id']}: {scene['title']}."
                fixed_scenes.append(scene)
            return fixed_scenes

        print("Generating visualization plan...")
        
       
        try:
            response_text = self.ollama.generate_text(base_prompt, system_prompt=system_prompt)
            scenes_list = extract_json_array(response_text)
            scenes_list = validate_and_fix_scenes(scenes_list)
            return {"scenes": scenes_list}
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"JSON Parsing failed: {e}")
            if 'response_text' in locals() and response_text:
                print(f"Raw response (first 100 chars): {response_text[:100]}...")
            
            # RETRY MECHANISM
            print("Retrying with stricter prompt...")
            retry_prompt = base_prompt + "\n\nYOUR PREVIOUS OUTPUT WAS INVALID. OUTPUT ONLY A VALID JSON ARRAY STARTING WITH '[' AND ENDING WITH ']'."
            
            try:
                response_text = self.ollama.generate_text(retry_prompt, system_prompt=system_prompt)
                scenes_list = extract_json_array(response_text)
                scenes_list = validate_and_fix_scenes(scenes_list)
                return {"scenes": scenes_list}
            except Exception as e2:
                 print(f"Retry failed: {e2}")
                 
                 # FALLBACK STRATEGY (PRD 10.1)
                 print("--- Fallback: Attempting Simplified Visualization Plan ---")
                 simplified_prompt = f"""
                 The complex visualization plan failed. Please provide a SINGLE summary scene.
                 
                 CODE:
                 {code}
                 
                 EXPLANATION:
                 {explanation}
                 
                 OUTPUT ONLY a JSON array with exactly ONE scene.
                 The scene MUST have:
                 - "scene_id": 1
                 - "title": "Summary"
                 - "actions": [ {{"type": "show_text", "text": "..."}} ]
                 - "narration_text": "A brief summary of what the code does."
                 """
                 try:
                     response_text = self.ollama.generate_text(simplified_prompt, system_prompt=system_prompt)
                     scenes_list = extract_json_array(response_text)
                     scenes_list = validate_and_fix_scenes(scenes_list)
                     print("Simplified fallback successful.")
                     return {"scenes": scenes_list}
                 except Exception as e3:
                     print(f"Simplified fallback failed: {e3}")
                     return {"scenes": []}

        except Exception as e:
            print(f"Unexpected error: {e}")
            return {"scenes": []}
