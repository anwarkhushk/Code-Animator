
# PRD.md — AI Code Animator (Offline Educational Video Generator)

## Product Name
AI Code Animator — Offline Code-to-Video Explainer

## 1. Product Overview
AI Code Animator is an offline educational system that converts source code into narrated whiteboard-style videos explaining program execution step-by-step.

The system supports multiple programming languages including Python, Java, C, C++, JavaScript, TypeScript, Go, Rust, C#, Kotlin, and more. It automatically detects the language from file extensions or code content.

The system operates entirely without internet connectivity and generates teaching-quality visualizations for:
- Basic programming concepts
- Data Structures & Algorithms (DSA)
- Machine Learning algorithms

### Core Technologies
- Ollama — Code understanding & explanation (offline LLM)
- Whiteboard Renderer — Visualization engine
- pyttsx3 — Offline narration (Text-to-Speech)
- MoviePy — Video composition

---

## 2. Objectives

### Primary Goal
Automatically generate educational videos that visually and verbally explain how code executes.

### Secondary Goals
- Improve conceptual understanding
- Provide teaching-quality animations
- Enable offline AI-powered learning tools

---

## 3. Target Users
- Students learning programming
- Educators creating lecture material
- Self-learners preparing for interviews
- Beginners in Machine Learning

---

## 4. System Pipeline

Input Code
→ Code Explanation (Ollama)
→ Visualization Planning
→ Scene Generation
→ Whiteboard Rendering
→ Narration Generation
→ Video Composition
→ Final Educational Video (MP4)

---

## 5. Supported Code Categories

### 5.1 Simple Programs
Examples:
- Variable assignment
- Arithmetic operations
- Conditionals
- Loops
- Print/output statements

Visualization Strategy:
- Variable boxes with values
- Step-wise value updates
- Loop iteration counters
- Output display panel

---

### 5.2 Data Structures & Algorithms (DSA)

Supported Algorithms:
- Sorting (Bubble, Selection, Insertion)
- Searching (Linear, Binary)
- Recursion (Factorial, Fibonacci)
- Arrays and pointer-based operations

Visualization Requirements:
- Centered array layout
- Highlighted comparisons
- Swap animations
- Pointer movement
- Recursion stack visualization

---

### 5.3 Machine Learning Algorithms

Supported Algorithms:
- Linear Regression
- Logistic Regression
- Gradient Descent
- K-Means Clustering

Visualization Requirements:
- Scatter plots and graphs
- Best-fit line animation
- Loss curve visualization
- Cluster formation and centroid movement

---

## 6. Whiteboard Design Principles

Teaching-Quality Visual Standards:

Color Hierarchy:
- Background: Warm white
- Variables: Soft blue boxes
- Highlights: Pastel yellow
- Text: Soft black

Layout Zones:
Top: Step Title
Left: Variables Panel
Center: Main Visualization
Bottom: Explanation Text

---

## 7. Narration Requirements
- Clear explanation of each step
- Synchronization with visuals
- Beginner-friendly language
- Fully offline TTS

---

## 8. Video Output Requirements
- Format: MP4
- Resolution: 720p default (1080p optional)
- Scene-based animation
- Synced narration
- Smooth transitions

---

## 9. Functional Requirements
The system MUST:
- Operate fully offline
- Support simple, DSA, and ML code
- Produce deterministic visualizations
- Handle failures gracefully

---

## 10. Reliability & Failure Handling Requirements (NEW)

### 10.1 Visualization Planning Reliability
The system MUST generate at least one valid scene for supported code.
If planning fails:
- Retry with simplified prompt
- Use fallback planning strategy

### 10.2 Fail-Stop Pipeline Behavior
If no scenes are generated:
Abort execution
Display error
Do not generate video

Blank videos MUST never be produced.

### 10.3 Two-Stage Visualization Planning
Stage 1 — Generate execution steps (plain text)
Stage 2 — Convert steps to scene instructions

### 10.4 Narration Integrity
Narration generation must occur only if scenes exist.
Each scene must include narration text and visuals.

### 10.5 Output Validation
Before rendering:
- Ensure scenes > 0
- Ensure narration exists
If validation fails → stop pipeline.

---

## 11. Diagnostic Logging
Required logs:
- Visualization planning status
- Scene count
- Narration status
- Rendering progress

---

## 12. Definition of Successful Output
A valid video MUST contain:
- Visual animations
- Narration audio
- Step alignment
- Educational clarity

If any component is missing → output is invalid.

---

## 13. Future Enhancements
- GUI interface
- Interactive playback controls
- Step-by-step navigation
- Code editor integration

---

## 14. Key Innovation
AI Code Animator is unique because it:
- Works completely offline
- Focuses on pedagogical clarity
- Automatically converts code into teaching videos

