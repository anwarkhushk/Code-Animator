import pyttsx3
import os
import hashlib
import time
import wave

class NarrationEngine:
    def __init__(self, rate=150, volume=1.0):
        self.rate = rate
        self.volume = volume

    def generate_audio(self, text, output_dir):
        """Generates audio file with logging."""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        filename = hashlib.md5(text.encode()).hexdigest() + ".wav"
        output_path = os.path.join(output_dir, filename)
        
        if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
            print(f"[Audio] Using cached audio: {output_path}")
            return output_path

        print(f"[Audio] Generating audio for: {text[:30]}...")
        try:
            # Re-initialize engine for each call to avoid event loop hangs in some envs
            engine = pyttsx3.init()
            engine.setProperty('rate', self.rate)
            engine.setProperty('volume', self.volume)
            
            # Select voice if possible
            voices = engine.getProperty('voices')
            if voices:
                selected_voice = None
                for voice in voices:
                    if "Zira" in voice.name or "English" in voice.name:
                        selected_voice = voice.id
                        break
                if selected_voice:
                    engine.setProperty('voice', selected_voice)
            
            engine.save_to_file(text, output_path)
            engine.runAndWait()
            
            # Verify file exists and has size
            if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                print(f"[Audio] Successfully generated: {output_path}")
                return output_path
            else:
                raise Exception("File not created or empty (size < 1KB)")

        except Exception as e:
            print(f"[Audio] Error generating audio with pyttsx3: {e}")
            print("[Audio] Falling back to silent audio.")
            return self.create_silent_wav(output_path)

    def create_silent_wav(self, path, duration=2.0):
        try:
            with wave.open(path, 'w') as f:
                f.setnchannels(1)
                f.setsampwidth(2)
                f.setframerate(44100)
                n_frames = int(44100 * duration)
                f.writeframes(b'\x00' * n_frames * 2)
            print(f"[Audio] Generated silent audio: {path}")
            return path
        except Exception as e:
            print(f"[Audio] Error creating silent wav: {e}")
            return None
