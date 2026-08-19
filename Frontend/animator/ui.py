from __future__ import annotations

import datetime as dt
import threading
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox

from PIL import Image, ImageTk
import customtkinter as ctk

from animator.pipeline import CodeAnimationPipeline
import cv2
import subprocess
import sys
import pygame

# Initialize pygame mixer for audio
try:
    pygame.mixer.init()
except Exception:
    pass


class CodeAnimatorApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Code Animator")
        self.geometry("1200x760")
        self.configure(fg_color="#212121")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.current_code = ""
        self.last_video: Path | None = None
        self.running = False
        
        # Video state
        self.cap = None
        self.playing = False
        self.after_id = None
        self.current_time = 0.0
        self.video_duration = 0.0
        self.video_fps = 30.0
        self.audio_on = True

        self._build_layout()

    def _build_layout(self) -> None:
        header = ctk.CTkFrame(self, fg_color="#1A1A1A", corner_radius=14)
        header.pack(fill="x", padx=20, pady=(18, 8))
        ctk.CTkLabel(
            header,
            text="Code Animator",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="#00D4FF",
        ).pack(side="left", padx=16, pady=12)
        ctk.CTkLabel(
            header,
            text="Code-to-Video Studio",
            font=ctk.CTkFont(size=14),
            text_color="#A3A3A3",
        ).pack(side="left", padx=(0, 10))

        # Video Display Area
        self.video_frame = ctk.CTkFrame(self, fg_color="#171717", corner_radius=12, border_width=1, border_color="#2F2F2F")
        self.video_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.video_label = ctk.CTkLabel(self.video_frame, text="")
        self.video_label.pack(fill="both", expand=True, padx=10, pady=(10, 0))
        
        self.video_controls = ctk.CTkFrame(self.video_frame, fg_color="transparent")
        self.video_controls.pack(fill="x", padx=10, pady=10)
        
        self.play_btn = ctk.CTkButton(self.video_controls, text="Play", width=60, command=self.play_video)
        self.play_btn.pack(side="left", padx=5)
        
        self.pause_btn = ctk.CTkButton(self.video_controls, text="Pause", width=60, command=self.pause_video)
        self.pause_btn.pack(side="left", padx=5)

        self.vol_btn = ctk.CTkButton(self.video_controls, text="Vol: On", width=60, command=self.toggle_volume)
        self.vol_btn.pack(side="left", padx=5)
        
        self.timeline_slider = ctk.CTkSlider(self.video_controls, from_=0.0, to=1.0, command=self.seek_video)
        self.timeline_slider.pack(side="left", fill="x", expand=True, padx=10)
        self.timeline_slider.set(0)

        bottom = ctk.CTkFrame(self, fg_color="#1A1A1A", corner_radius=14)
        bottom.pack(fill="x", padx=20, pady=(0, 16))

        self.code_input = ctk.CTkTextbox(
            bottom,
            height=150,
            corner_radius=10,
            fg_color="#141414",
            border_width=1,
            border_color="#323232",
            font=ctk.CTkFont(family="Consolas", size=13),
        )
        self.code_input.pack(fill="x", padx=14, pady=(14, 10))

        actions = ctk.CTkFrame(bottom, fg_color="transparent")
        actions.pack(fill="x", padx=14, pady=(0, 8))

        self.fps_var = ctk.StringVar(value="2")
        ctk.CTkLabel(actions, text="FPS", text_color="#9E9E9E").pack(side="left", padx=(0, 8))
        ctk.CTkOptionMenu(actions, values=["1", "2", "3", "5", "8"], variable=self.fps_var, width=70).pack(side="left")

        ctk.CTkButton(actions, text="Load Code", command=self.load_code, width=110).pack(side="left", padx=8)
        self.make_video_btn = ctk.CTkButton(actions, text="Make Video", command=self.make_video, width=100)
        self.make_video_btn.pack(side="left", padx=8)

        self.progress = ctk.CTkProgressBar(bottom, progress_color="#00D4FF")
        self.progress.pack(fill="x", padx=14, pady=(6, 12))
        self.progress.set(0)

        self.status = ctk.CTkLabel(bottom, text="Idle", anchor="w", text_color="#A3A3A3")
        self.status.pack(fill="x", padx=14, pady=(0, 12))

    def set_status(self, text: str) -> None:
        self.status.configure(text=text)

    def load_code(self) -> None:
        file_path = filedialog.askopenfilename(filetypes=[
            ("All Code Files", "*.py *.java *.c *.cpp *.cc *.cxx *.h *.hpp *.js *.ts *.go *.rs *.rb *.cs *.kt *.swift *.php *.scala *.lua *.pl *.sh *.dart"),
            ("Python", "*.py"),
            ("Java", "*.java"),
            ("C", "*.c *.h"),
            ("C++", "*.cpp *.cc *.cxx *.hpp"),
            ("JavaScript", "*.js"),
            ("TypeScript", "*.ts"),
            ("Go", "*.go"),
            ("Rust", "*.rs"),
            ("C#", "*.cs"),
            ("All files", "*.*"),
        ])
        if not file_path:
            return
        code = Path(file_path).read_text(encoding="utf-8")
        self.current_code = code
        self._loaded_file_path = file_path
        self.code_input.delete("1.0", "end")
        self.code_input.insert("1.0", code)
        self.set_status(f"Loaded file: {file_path}")

    def make_video(self) -> None:
        if self.running:
            return
        code = self.code_input.get("1.0", "end").strip()
        if not code:
            self.set_status("Please enter or load code before making video.")
            return

        self.running = True
        self.make_video_btn.configure(state="disabled")
        self.progress.set(0.1)
        self.set_status("Running pipeline...")

        def worker() -> None:
            try:
                # 1. Write the code editor contents to a temporary file
                # Detect language from loaded file or code content to choose correct temp extension
                from pathlib import Path
                import sys
                import subprocess
                
                # Resolve the project root dynamically Based on ui.py location 
                # (Frontend/animator/ui.py -> CodeAnimator)
                project_root = Path(__file__).resolve().parent.parent.parent
                
                if str(project_root) not in sys.path:
                    sys.path.insert(0, str(project_root))
                
                from utils.language_detect import detect_language, get_temp_extension
                _loaded_path = getattr(self, '_loaded_file_path', None)
                _lang = detect_language(file_path=_loaded_path, code=code)
                _ext = get_temp_extension(_lang)
                
                temp_input = project_root / f"temp_input_code{_ext}"
                temp_input.write_text(code, encoding="utf-8")
                
                # 2. Determine the path to the main pipeline script and output
                main_script = project_root / "main_pipeline.py"
                
                # Ensure output directory exists
                output_dir = project_root / "output"
                output_dir.mkdir(exist_ok=True)
                
                output = output_dir / "final_video.mp4"
                
                if output.exists():
                    try:
                        output.unlink() # remove old output if it exists
                    except Exception:
                        pass
                
                # 3. Simulate progress updates
                self.after(0, lambda: self.progress.set(0.3))
                self.after(0, lambda: self.set_status("Running AI Explanation & Scene Generation..."))
                
                # 4. Run main_pipeline.py as a subprocess
                result = subprocess.run(
                    [sys.executable, str(main_script), str(temp_input), "--output", str(output)],
                    cwd=str(project_root),
                    capture_output=True,
                    text=True
                )
                
                # 5. Handle output results
                if result.returncode != 0 or not output.exists():
                    error_msg = result.stderr if result.stderr else result.stdout
                    raise Exception(f"Pipeline failed:\n{error_msg[-200:]}")
                
                # Cleanup temp file
                if temp_input.exists():
                    try:
                        temp_input.unlink()
                    except Exception:
                        pass

                self.last_video = output
                self.after(0, lambda o=output: self._on_success(o))
            except Exception as exc:  # noqa: BLE001
                self.after(0, lambda e=exc: self._on_error(e))

        threading.Thread(target=worker, daemon=True).start()

    def _on_success(self, video_path: Path) -> None:
        self.progress.set(1)
        self.set_status(f"Completed • {video_path}")
        self.make_video_btn.configure(state="normal")
        self.running = False
        self.load_video(video_path)

    def _on_cancel(self) -> None:
        self.progress.set(0)
        self.set_status("Cancelled")
        self.make_video_btn.configure(state="normal")
        self.running = False

    def _on_error(self, exc: Exception) -> None:
        self.progress.set(0)
        self.set_status("Failed")
        self.make_video_btn.configure(state="normal")
        self.running = False

    def load_video(self, video_path: Path) -> None:
        self.stop_video()
        try:
            self.cap = cv2.VideoCapture(str(video_path))
            self.video_fps = self.cap.get(cv2.CAP_PROP_FPS)
            frame_count = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
            self.video_duration = frame_count / self.video_fps if self.video_fps > 0 else 0
            self.current_time = 0.0
            
            # Load audio explicitly (Pygame can't natively stream nested MP4 audio formats smoothly)
            try:
                from moviepy import VideoFileClip
                mpy_clip = VideoFileClip(str(video_path))
                if mpy_clip.audio is not None:
                    audio_path = str(video_path) + ".mp3"
                    mpy_clip.audio.write_audiofile(audio_path, logger=None)
                    pygame.mixer.music.load(audio_path)
                else:
                    pygame.mixer.music.load(str(video_path))
                mpy_clip.close()
            except Exception as e:
                print(f"Audio Load Warning: {e}")

            self.timeline_slider.configure(from_=0.0, to=self.video_duration)
            self._update_frame(0.0)
            self.play_video()
        except Exception as e:
            self.set_status(f"Error loading video: {e}")

    def _update_frame(self, t: float) -> None:
        if not hasattr(self, 'cap') or not self.cap or not self.cap.isOpened():
            return
        try:
            # seek to frame
            frame_number = int(t * self.video_fps)
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = self.cap.read()
            if not ret:
                return
            
            # Convert BGR to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame)
            
            width = self.video_label.winfo_width()
            height = self.video_label.winfo_height()
            if width > 10 and height > 10:
                image.thumbnail((width, height), Image.Resampling.LANCZOS)
            
            pimg = ImageTk.PhotoImage(image)
            self.video_label.configure(image=pimg, text="")
            self.video_label.image = pimg
            self.timeline_slider.set(t)
            self.current_time = t
        except Exception:
            pass

    def play_video(self) -> None:
        if not hasattr(self, 'cap') or not self.cap or not self.cap.isOpened() or self.playing:
            return
        self.playing = True
        
        # Audio Playback Handling
        try:
            # If current time is almost zero, play from beginning
            if getattr(self, "audio_started", False) is False or self.current_time < 0.1:
                pygame.mixer.music.play()
                pygame.mixer.music.set_pos(self.current_time)
                self.audio_started = True
            else:
                pygame.mixer.music.unpause()
        except Exception:
            pass

        self._play_loop()

    def _play_loop(self) -> None:
        if not self.playing or not hasattr(self, 'cap') or not self.cap or not self.cap.isOpened():
            return
            
        self._update_frame(self.current_time)
        step = 1.0 / self.video_fps if self.video_fps > 0 else 1.0 / 30.0
        self.current_time += step
        
        if self.current_time > self.video_duration:
            self.playing = False
            self.current_time = 0.0
            self.audio_started = False
            self._update_frame(0.0)
            
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass
            return
            
        self.after_id = self.after(int(step * 1000), self._play_loop)

    def pause_video(self) -> None:
        self.playing = False
        try:
            pygame.mixer.music.pause()
        except Exception:
            pass

        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None

    def seek_video(self, value: float) -> None:
        if not hasattr(self, 'cap') or not self.cap or not self.cap.isOpened():
            return
        self.current_time = float(value)
        self._update_frame(self.current_time)
        
        try:
            if self.playing:
                pygame.mixer.music.set_pos(self.current_time)
            else:
                # If paused when seeking, make sure music starts from right place when unpaused later
                pygame.mixer.music.play()
                pygame.mixer.music.set_pos(self.current_time)
                pygame.mixer.music.pause()
                self.audio_started = True
        except Exception:
            pass

    def toggle_volume(self) -> None:
        self.audio_on = not self.audio_on
        if self.audio_on:
            self.vol_btn.configure(text="Vol: On")
            try:
                pygame.mixer.music.set_volume(1.0)
            except Exception:
                pass
        else:
            self.vol_btn.configure(text="Vol: Off")
            try:
                pygame.mixer.music.set_volume(0.0)
            except Exception:
                pass

    def stop_video(self) -> None:
        self.pause_video()
        try:
            pygame.mixer.music.stop()
            self.audio_started = False
        except Exception:
            pass

        if hasattr(self, 'cap') and self.cap:
            self.cap.release()
            self.cap = None
        self.video_label.configure(image="")


def run_app() -> None:
    app = CodeAnimatorApp()
    app.mainloop()
