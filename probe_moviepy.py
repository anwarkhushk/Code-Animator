
import moviepy
import inspect

print(f"MoviePy Version: {moviepy.__version__}")

def find_symbol(name, module):
    if hasattr(module, name):
        return f"{module.__name__}.{name}"
    
    # naive recursive search in submodules usually not safe, but let's try top level dir
    return None

needed = [
    'ImageClip', 
    'CompositeVideoClip', 
    'concatenate_videoclips', 
    'AudioFileClip', 
    'VideoFileClip'
]

# Try to find them in moviepy directly
print("Checking top-level moviepy...")
for n in needed:
    if hasattr(moviepy, n):
       print(f"Found {n} in moviepy")
    else:
       print(f"Did NOT find {n} in moviepy")

# Try to find substructure
try:
    import moviepy.video.io.ImageSequenceClip
    print("moviepy.video.io.ImageSequenceClip imported")
except ImportError:
    print("moviepy.video.io.ImageSequenceClip failed")

try:
    from moviepy.video.compositing import concatenate
    print("moviepy.video.compositing.concatenate imported")
except ImportError:
    print("moviepy.video.compositing.concatenate failed")

