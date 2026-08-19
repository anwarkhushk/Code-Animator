import ollama
import json

class OllamaClient:
    def __init__(self, model="deepseek-coder:6.7b"):
        self.model = model
        # Test connection strictly
        try:
            ollama.list()
        except Exception as e:
            print(f"Warning: Could not connect to Ollama: {e}")

    def generate_text(self, prompt, system_prompt=None):
        """Generates plain text response."""
        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        messages.append({'role': 'user', 'content': prompt})

        try:
            response = ollama.chat(model=self.model, messages=messages)
            return response['message']['content']
        except Exception as e:
            print(f"Error generating text: {e}")
            return None

    def generate_json(self, prompt, system_prompt=None):
        
        
        full_prompt = prompt + "\n\nIMPORTANT: Output ONLY valid JSON."
        if system_prompt:
            system_prompt += " You must output valid JSON only."
        
        text = self.generate_text(full_prompt, system_prompt)
        if not text:
            return None
            
        # Try to find JSON block
        try:
            # 1. Try regex for ```json ... ``` or just ``` ... ```
            import re
            code_block_pattern = re.compile(r"```(?:json)?\s*({.*?})\s*```", re.DOTALL)
            match = code_block_pattern.search(text)
            if match:
                json_str = match.group(1)
                return json.loads(json_str)

            # 2. Try finding the outer-most braces
            start = text.find('{')
            end = text.rfind('}')
            if start != -1 and end != -1:
                json_str = text[start:end+1]
                return json.loads(json_str)
                
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            with open("debug_response.txt", "w", encoding="utf-8") as f:
                f.write(text)
            print("Saved raw response to debug_response.txt")
            pass
            
        print(f"Could not extract JSON from response. Length: {len(text)}")
        return None
