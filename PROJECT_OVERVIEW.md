# AI Code Animator - Project Overview & Progress Report

## 1. Project Overview
**AI Code Animator** is an offline, AI-powered educational system that converts source code into narrated whiteboard-style explainer videos. It is designed to help students, educators, and self-learners by automatically generating visual step-by-step executions of programming concepts, Data Structures & Algorithms (DSA), and Machine Learning (ML) algorithms.

**Supported Languages:** Python, Java, C, C++, JavaScript, TypeScript, Go, Rust, C#, Kotlin, Ruby, and more.

**Key Features:**
- **Multi-Language Support:** Automatically detects the programming language from file extensions or code content, and generates tailored explanations and visualizations.
- **Fully Offline Execution:** Utilizes local LLMs and TTS engines, ensuring deep privacy and no dependency on external APIs.
- **Pedagogical Focus:** Generates teaching-quality visualizations and dynamically synced narrations.
- **Broad Conceptual Support:** Capable of visualizing everything from basic variable assignments to complex ML models like K-Means Clustering and Gradient Descent.

## 2. Core Technologies
- **Ollama:** Code understanding and visualization planning (runs local models like DeepSeek-Coder).
- **Whiteboard Renderer:** A custom Python-based visualization engine rendering state to image frames.
- **pyttsx3:** Offline Text-to-Speech (TTS) for educational narration.
- **MoviePy:** Video composition, combining rendered whiteboard frames and synchronized audio clips.

## 3. System Architecture & Workflow

The system processes source code through a sequence of discrete steps, managed entirely by `main_pipeline.py`:

1. **Input Code**: The user provides a target source code file (Python, Java, C, C++, JavaScript, etc.).
2. **Language Detection**: The system automatically detects the programming language from the file extension or code content (`utils/language_detect.py`).
3. **Code Explanation (`VisualizationBrain`)**: The code and detected language are sent to the local Ollama LLM to generate a plain-text, step-by-step educational explanation of the algorithm's execution logic.
3. **Visualization Planning (`VisualizationBrain`)**: The LLM converts the text explanation into a structured JSON plan. This plan consists of an array of "scenes." Each scene includes a `narration_text` string and a set of `actions` (specific visual instructions like `draw_variable`, `draw_array`, `highlight_cell`, `draw_point`).
4. **Output Validation**: The pipeline validates the generated JSON to ensure it is not empty and contains mandatory fields. Strict fail-stop mechanisms abort the pipeline if planning completely fails.
5. **Asset Generation**:
   - **Audio (`NarrationEngine`)**: Converts the step's narration text into audio files.
   - **Video Frames (`WhiteboardRenderer`)**: Executes the visual actions to sequentially draw and update variables, arrays, pointers, and ML graphs onto the canvas.
6. **Video Composition (`VideoComposer`)**: Merges the generated audio explanations with the rendered whiteboard frames into a final `.mp4` video (supporting both 720p and 1080p outputs).

## 4. Current Progress & Completed Features

Based on `progress.txt` and the system specifications, the core pipeline is fully functional with extensive support for advanced visualizations.

### 🟢 Core Infrastructure
- Two-stage visualization planning via `VisualizationBrain` for stable JSON outputs.
- Robust error handling, output validation, and JSON parsing with simplified fallback strategies.
- Complete audio and video compilation pipeline.
- Enhanced diagnostic logging for pipeline progress and health tracking.

### 🟢 Simple Programs & Base Concepts
- Variable assignment and state tracking (`draw_variable`, `update_value`).
- Explaining program flow, conditionals, and console outputs.

### 🟢 Data Structures & Algorithms (DSA)
- **Arrays & Pointers:** High-quality layouts for arrays (`draw_array`), cell highlights (`highlight_cell`), index pointers (`draw_pointer`, `move_pointer`), and swapping values (`swap_cells`).
- **Algorithms:** Bubble Sort, comparisons, and Search algorithms.
- **Recursion:** Support for recursive stack visualizations (e.g., Fibonacci execution).

### 🟢 Machine Learning Visualizations
- **Linear Regression & Gradient Descent:** Full support for rendering scatter plots (`draw_point`), drawing lines (`draw_line`), and updating regression slopes/intercepts.
- **Logistic Regression:** Support for visually rendering the Sigmoid function and classification boundaries.
- **K-Means Clustering:** Complex visualizers for mapping data points in designated clusters and dynamically updating centroid positions (`update_clusters`).

### 🟢 Graphical User Interface (GUI) & Playback Integration
- **CustomTkinter UI:** A sleek, fully functional dark-themed frontend (`Frontend/app.py` & `Frontend/animator/ui.py`) featuring a dedicated code editor and video player area.
- **Background Threading:** Seamlessly generates the video via `main_pipeline.py` in the background without freezing the application interface.
- **Native Video Player:** Integrated OpenCV (`cv2`) for exact frame-by-frame video rendering directly onto the Tkinter canvas using `PIL`.
- **Synchronized Audio Tracking:** Utilizes `moviepy` to natively extract `.mp4` audio sequences and maps them perfectly to a `pygame.mixer` instance for synchronized sound and video playback. Includes interactive Timeline Seeking, Play/Pause, and a native Volume Toggle.

## 5. Setup & Usage

The system can now be run entirely through the local application frontend!

To launch the GUI, simply run:
```bash
python Frontend/app.py
```
From the GUI:
1. Click **Load Code** to select a target source code file (`.py`, `.java`, `.c`, `.cpp`, `.js`, etc.), or simply type code directly into the bottom editor.
2. Adjust the desired FPS.
3. Click **Make Video** to kick off the background generation pipeline.
4. Wait for processing to complete—the video will automatically load into the top player with synchronized audio!

*(The CLI can still be used via `python main_pipeline.py <file> --output <dest>` if needed).*

## 6. Future Enhancements
- Expand Machine Learning algorithm visualizers (e.g., Neural Networks, Decision Trees).
- Add interactive playback controls exported directly to the generated video artifacts.
- Support concurrent animation actions to further improve video pacing and aesthetic value.
