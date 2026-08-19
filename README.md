# Code Animator

**Code Animator** is an AI-powered educational tool that converts source code into **animated visualizations with explanations and narration**. It is designed to make programming concepts easier to understand by visually showing how code executes step by step.

## 🚀 Features

* 🤖 **AI-Powered Code Analysis** – Uses a local LLM to understand and analyze source code.
* 🎬 **Automatic Visualization** – Converts code execution into structured animation plans.
* 🧠 **DSA Visualizations** – Supports concepts such as arrays, searching, sorting, recursion, variables, and pointers.
* 📊 **ML Visualizations** – Supports visualization of concepts such as Linear Regression, Logistic Regression, and K-Means.
* 🎙️ **Offline Narration** – Generates voice narration using `pyttsx3`.
* 🎥 **Automatic Video Generation** – Combines visualizations and narration into an educational video.
* 🔒 **Offline Processing** – Uses a locally running LLM, reducing dependency on external APIs.
* 🛡️ **Error Handling & Fallbacks** – Handles invalid AI-generated responses through parsing, repair, re-prompting, and fallback mechanisms.

## 🏗️ How It Works

```text
Source Code
     ↓
AI Code Analysis
     ↓
Explanation Generation
     ↓
Visualization Plan
     ↓
Animation Generation
     ↓
Narration Generation
     ↓
Video Composition
     ↓
Educational Code Animation
```

## 🧩 Project Architecture

```text
Code Animator
│
├── UI
│   └── CustomTkinter Interface
│
├── Code Analysis
│   └── Local LLM
│
├── Visualization Brain
│   ├── Code Explanation
│   ├── Visualization Planning
│   └── JSON Validation / Repair
│
├── Visualization Engine
│   ├── DSA
│   └── Machine Learning
│
├── Narration
│   └── pyttsx3
│
└── Video Generation
    └── MoviePy
```

## 🛠️ Technologies Used

* **Python**
* **CustomTkinter**
* **Ollama**
* **DeepSeek-Coder / Local LLM**
* **MoviePy**
* **pyttsx3**
* **Matplotlib**
* **NumPy**
* **JSON**

## 📚 Supported Concepts

### Data Structures & Algorithms

* Arrays
* Variables
* Pointers
* Searching
* Bubble Sort
* Recursion
* Other basic DSA concepts

### Machine Learning

* Linear Regression
* Logistic Regression
* K-Means Clustering

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/your-username/code-animator.git
cd code-animator
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Make sure **Ollama** is installed and running locally, then pull the required model:

```bash
ollama pull deepseek-coder
```

Run the application:

```bash
python app.py
```

## 🎯 Usage

1. Open Code Animator.
2. Enter or load your source code.
3. Click **Load Code**.
4. Click **Make Video**.
5. The AI analyzes the code and generates an explanation.
6. A structured visualization plan is created.
7. The visualization and narration are generated automatically.
8. The final educational video is produced.

## 🔮 Future Improvements

* Support for more programming languages.
* More advanced DSA visualizations.
* Neural network and deep learning visualizations.
* Interactive step-by-step execution.
* Improved animation quality.
* Support for multiple narration voices.
* Web-based interface.
* More advanced AI-generated explanations.

## 👨‍💻 Project

**Code Animator** — Making complex programming concepts easier to understand through **AI-generated visualizations and narration**.
