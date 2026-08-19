#Execution tracing engine

#Frame generation logic

#Video encoding pipeline

#End-to-end processing flow


from __future__ import annotations

import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List


@dataclass
class TraceSnapshot:
    line_no: int
    code_line: str
    locals_state: Dict[str, str]


class TracingEngine:
    """Executes Python code and captures per-line state with sys.settrace."""

    def __init__(self, source_code: str) -> None:
        self.source_code = source_code
        self.lines = source_code.splitlines()
        self.snapshots: List[TraceSnapshot] = []

    def _trace(self, frame, event, arg):
        if event != "line":
            return self._trace

        if frame.f_code.co_filename != "<animated_code>":
            return self._trace

        line_no = frame.f_lineno
        code_line = self.lines[line_no - 1] if 0 < line_no <= len(self.lines) else ""
        safe_locals = {k: repr(v)[:120] for k, v in frame.f_locals.items() if not k.startswith("__")}
        self.snapshots.append(TraceSnapshot(line_no=line_no, code_line=code_line, locals_state=safe_locals))
        return self._trace

    def execute(self) -> List[TraceSnapshot]:
        compiled = compile(self.source_code, "<animated_code>", "exec")
        globals_ctx = {"__name__": "__main__"}
        sys.settrace(self._trace)
        try:
            exec(compiled, globals_ctx)
        finally:
            sys.settrace(None)
        return self.snapshots


class FrameComposer:
    """Generates PNG frames that include code and variable state."""

    BG_COLOR = "#121212"
    PANEL_COLOR = "#1e1e1e"
    ACCENT = "#00D4FF"
    TEXT = "#EAEAEA"
    MUTED = "#A6A6A6"
    HIGHLIGHT = "#2A2A2A"

    def __init__(self, width: int = 1280, height: int = 720) -> None:
        self.width = width
        self.height = height
        from PIL import Image, ImageDraw, ImageFont

        self.Image = Image
        self.ImageDraw = ImageDraw
        self.font = ImageFont.load_default()

    def _draw_header(self, draw: Any, step: int, total: int) -> None:
        draw.rectangle((0, 0, self.width, 50), fill=self.PANEL_COLOR)
        draw.text((20, 18), "Code Animator • Execution Timeline", font=self.font, fill=self.ACCENT)
        draw.text((self.width - 240, 18), f"Frame {step}/{total}", font=self.font, fill=self.MUTED)

    def _draw_code_panel(self, draw: Any, lines: List[str], active_line: int) -> None:
        x0, y0, x1, y1 = 20, 70, int(self.width * 0.67), self.height - 20
        draw.rounded_rectangle((x0, y0, x1, y1), radius=12, fill=self.PANEL_COLOR)
        draw.text((x0 + 14, y0 + 10), "Source Code", font=self.font, fill=self.ACCENT)

        top = y0 + 34
        for idx, line in enumerate(lines, start=1):
            y = top + (idx - 1) * 16
            if y > y1 - 20:
                break
            if idx == active_line:
                draw.rectangle((x0 + 10, y - 1, x1 - 10, y + 14), fill=self.HIGHLIGHT)
            draw.text((x0 + 14, y), f"{idx:>3}  {line}", font=self.font, fill=self.TEXT)

    def _draw_variables_panel(self, draw: Any, vars_state: Dict[str, str]) -> None:
        x0, y0, x1, y1 = int(self.width * 0.69), 70, self.width - 20, self.height - 20
        draw.rounded_rectangle((x0, y0, x1, y1), radius=12, fill=self.PANEL_COLOR)
        draw.text((x0 + 14, y0 + 10), "Variable Watch", font=self.font, fill=self.ACCENT)

        if not vars_state:
            draw.text((x0 + 14, y0 + 36), "No variables yet", font=self.font, fill=self.MUTED)
            return

        y = y0 + 36
        for key, value in vars_state.items():
            if y > y1 - 20:
                break
            draw.text((x0 + 14, y), f"{key} = {value}", font=self.font, fill=self.TEXT)
            y += 16

    def compose(self, output_dir: Path, source_code: str, snapshots: List[TraceSnapshot]) -> List[Path]:
        lines = source_code.splitlines()
        frames: List[Path] = []
        total = max(len(snapshots), 1)

        if not snapshots:
            snapshots = [TraceSnapshot(1, lines[0] if lines else "", {})]

        for step, snapshot in enumerate(snapshots, start=1):
            img = self.Image.new("RGB", (self.width, self.height), color=self.BG_COLOR)
            draw = self.ImageDraw.Draw(img)
            self._draw_header(draw, step, total)
            self._draw_code_panel(draw, lines, snapshot.line_no)
            self._draw_variables_panel(draw, snapshot.locals_state)
            path = output_dir / f"frame_{step:05d}.png"
            img.save(path)
            frames.append(path)
        return frames


class VideoEncoder:
    """Encodes image sequences into MP4 using MoviePy/FFmpeg."""

    def encode(self, frames: List[Path], output_path: Path, fps: int = 2) -> Path:
        from moviepy.video.io.ImageSequenceClip import ImageSequenceClip

        clip = ImageSequenceClip([str(frame) for frame in frames], fps=fps)
        clip.write_videofile(str(output_path), codec="libx264", audio=False, logger=None)
        clip.close()
        return output_path


@dataclass
class AnimationResult:
    output_video: Path
    frame_count: int


class CodeAnimationPipeline:
    """End-to-end pipeline for tracing, frame generation, and video export."""

    def __init__(self, progress_callback: Callable[[str], None] | None = None) -> None:
        self.progress_callback = progress_callback or (lambda _msg: None)
        self.tracer = TracingEngine
        self.composer = FrameComposer()
        self.encoder = VideoEncoder()

    def _notify(self, msg: str) -> None:
        self.progress_callback(msg)

    def run(self, source_code: str, output_path: Path, fps: int = 2) -> AnimationResult:
        self._notify("Starting secure trace execution...")
        snapshots = self.tracer(source_code).execute()
        self._notify(f"Captured {len(snapshots)} execution steps.")

        with tempfile.TemporaryDirectory(prefix="code_animator_") as temp_dir:
            temp_path = Path(temp_dir)
            self._notify("Composing PNG frames with Pillow...")
            frames = self.composer.compose(temp_path, source_code, snapshots)
            self._notify(f"Generated {len(frames)} frames.")

            self._notify("Encoding MP4 using MoviePy/FFmpeg...")
            video = self.encoder.encode(frames, output_path=output_path, fps=fps)

        self._notify("Cleanup complete. Temporary frames removed.")
        return AnimationResult(output_video=video, frame_count=len(snapshots))
