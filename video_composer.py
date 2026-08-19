from moviepy import *
import os

class VideoComposer:
    def __init__(self):
        pass

    def compose_video(self, scenes, audio_paths, video_clips, output_file):
        """
        Combines video clips and audio files into a final video.
        """
        
        final_clips = []
        print(f"Composing {len(video_clips)} clips into final video...")
        
        for i in range(len(video_clips)):
            if i >= len(audio_paths):
                break
                
            audio_path = audio_paths[i]
            video_clip = video_clips[i]
            
            print(f"[Composer] Attaching audio {os.path.basename(audio_path)} to clip {i}...")
            
            # Load audio
            try:
                audio_clip = AudioFileClip(audio_path)
                
                # Optimization: Short buffer
                scene_duration = audio_clip.duration + 0.2
                
                # Handle MoviePy v1 vs v2 compatibility
                try:
                    video_clip = video_clip.with_duration(scene_duration)
                    video_clip = video_clip.with_audio(audio_clip)
                except AttributeError:
                    video_clip = video_clip.set_duration(scene_duration)
                    video_clip = video_clip.set_audio(audio_clip)
                
                final_clips.append(video_clip)
            except Exception as e:
                print(f"[Composer] Error attaching audio for clip {i}: {e}")
                # Fallback: keep video as is, maybe default duration
                final_clips.append(video_clip)
            
        print(f"Concatenating {len(final_clips)} clips...")
        try:
            final_video = concatenate_videoclips(final_clips, method="compose")
            
            print(f"Writing optimized video to {output_file}...")
            
            # Optimization: Use 'ultrafast' preset and multiple threads
            final_video.write_videofile(
                output_file, 
                fps=24, 
                codec='libx264', 
                audio_codec='aac',
                preset='ultrafast',
                threads=4,
                temp_audiofile='temp-audio.m4a',
                remove_temp=True
            )
            print("[Composer] Video composition complete.")
            
        except Exception as e:
             print(f"[Composer] Error during encoding: {e}")
