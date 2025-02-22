
from langchain_core.tools import tool
from moviepy import VideoFileClip, AudioFileClip, CompositeVideoClip
from langchain_community.tools import TavilySearchResults
from pydantic import BaseModel, Field
import os
import requests
import pyttsx3
import time
import subprocess
from environ import secrets
from server.tools import add_audio_to_video

secrets()


def run_script(file_name: str, script_class: str, audio_file: str):
    """run the manim script you just made. To use this tool, input the file name the write_script tool just made and nothing else. You also need to input the main class that runs the whole scene"""
    print(f"We are running {file_name} with class {script_class}")

    file_path = f"generated_video_code\\{file_name}"
    audio_path = f"generated_audio\\{audio_file}"

    command = [
        "manim", "-pqh", f"{file_path}", f"{script_class}"
    ]

    try:
        print('a')
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,encoding='utf-8')
        print("The video was successfully generated!")

        # Prepare the data to post
        base_name = os.path.splitext(file_name)[0]
        data_to_post = base_name + f"/1080p60/" + script_class + ".mp4"

        cd = os.getcwd()

        videos_dir = cd + "\\media\\videos"

        video = os.path.join(videos_dir, data_to_post)

        save = os.path.join(videos_dir, data_to_post.replace(".mp4", "tts_exp.mp4"))

        time.sleep(10)

        add_audio_to_video(
            video_path=video,
            audio_path=audio_path,
            output_path=save
        )

        data_to_post = base_name + f"/1080p60/" + script_class + "tts_exp" + ".mp4"


        data = {"filename": data_to_post}
        response = requests.post(url = "http://127.0.0.1:5000/get_video", json=data)

        if response.status_code == 200:
            print("Video served successfully")
        else:
            print(f"Error: {response.status_code}")
            return f"Error: {response.status_code}"
    except subprocess.CalledProcessError as e:
        print("Subprocess failed with exit code:", e.returncode)
        print("Subprocess STDOUT:\n", e.stdout)
        print("Subprocess STDERR:\n", e.stderr)

    except Exception as e:
        print(str(e))
        return {"status": "error", "message": str(e)}
#run_script('integral_visualization.py', 'IntegralVisualization', 'integral.mp3')
#run_script('eulers_theorem_fixed.py', 'EulerTheoremFixed', 'eulers_theorem.mp3')
run_script('RiemannSumVisualization.py', 'RiemannSumVisualization', 'RiemannSum.mp3')