import cv2
import numpy as np
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
secrets()
from generated_video_code import integral_visualization
import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont, ImageGrab
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase
import av
from reportlab.pdfgen import canvas

@tool()
def explain_screenshot():
    """
    Generate a list of steps to complete the math problem on a screenshot
    """

@tool("take_screenshot")
def take_screenshot():
    """
    Take a screenshot of the user's math problem, crop the image to where the user drew a red box, and save the image.
    """
    screenshot = ImageGrab.grab()

def crop_screenshot(screenshot):
    x, y, w, h = detect_red_rectangle(screenshot)

def detect_red_rectangle(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    lower_red = np.array([0, 100, 100])
    upper_red = np.array([10, 255, 255])
    mask1 = cv2.inRange(hsv, lower_red, upper_red)

    lower_red = np.array([170, 100, 100])
    upper_red = np.array([180, 255, 255])
    mask2 = cv2.inRange(hsv, lower_red, upper_red)

    mask = mask1 + mask2

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        return x, y, w, h
    return None

@tool("handwrite_on_pdf")
def handwrite_on_pdf(file_path: str = None, output_path: str = "handwritten_output.pdf", text: str = "Hello!",
                     x: int = 100, y: int = 100, font_path: str = "handwriting_font.ttf", font_size: int = 36):
    """
    Simulate handwriting on a PDF using a handwriting font.

    Args:
        file_path (str, optional): Path to existing PDF. Creates a new PDF if None.
        output_path (str): Path to save the modified PDF.
        text (str): Text to simulate as handwritten.
        x, y (int): Coordinates to place the text.
        font_path (str): Path to handwriting font (e.g., .ttf file).
        font_size (int): Size of the handwritten text.
    """
    try:
        print(text)
        print(output_path)

        # Create or open PDF
        if file_path:
            pdf = fitz.open(file_path)
            page = pdf[0]
        else:
            pdf = fitz.open()
            page = pdf.new_page()

        # Create handwritten text image
        font = ImageFont.truetype(font_path, font_size)
        image = Image.new("RGBA", (800, 200), (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)
        draw.text((10, 10), text, font=font, fill=(0, 0, 0))

        # Save image temporarily
        temp_image_path = f"input_pdf\\temp_handwriting.png"
        image.save(temp_image_path)

        # Insert image into PDF
        rect = fitz.Rect(x, y, x + image.width, y + image.height)
        page.insert_image(rect, filename=temp_image_path)

        # Save PDF
        pdf.save(f"generated_pdf\\{output_path}")
        pdf.close()

        return f"Handwritten text added to PDF and saved to {output_path}"

    except Exception as e:
        return f"Error while handwriting on PDF: {str(e)}"


def add_audio_to_video(video_path, audio_path, output_path):
    """
    Add audio to a video file using basic MoviePy functionality
    """
    try:
        print(f"Loading video from: {video_path}")
        video = VideoFileClip(video_path)
        
        print(f"Loading audio from: {audio_path}")
        audio = AudioFileClip(audio_path)
        
        # Create new video with audio
        print("Combining audio and video...")
        final_video = video.copy()
        final_video.audio = audio
        
        # Write output
        final_video.write_videofile(
            output_path,
            temp_audiofile="temp-audio.m4a",
            remove_temp=True,
            codec="libx264", 
            audio_codec="aac"
        )
        
        # Clean up
        video.close()
        audio.close()
        final_video.close()
        
        print("Successfully combined audio and video!")
        
    except Exception as e:
        print(f"Error in add_audio_to_video: {str(e)}")
        # Make sure to clean up even if there's an error
        try:
            video.close()
            audio.close()
        except:
            pass
        raise



class writeScript(BaseModel):
    file_name: str = Field(description="The filename of the manim script you just made. It should be XXX.py")
    script: str = Field(description="The script to write for generating the manim animation. Must be in proper python syntax")

@tool("write_script", args_schema=writeScript)
def write_script(file_name: str, script: str):
    """Write and save the python script for generating the manim animation. The script must be in proper python syntax for it to work
    Use Reference example: class IntegralVisualization
    THIS IS IMPORTANT: When writing script write the self.play for the title like: self.play(title.animate.to_edge(UP))
    When using "\theta" in any text, make sure you use "\\theta" instead because python will interpret "\t" as a tab
    Also make sure you run into no manim errors or latex errors, take your time and write the code carefully and step by step
    Also when making latex like Tex("if $\gcd(a, n) = 1$") add a r in front of the string like Tex(r"if $...")

  """


    print("HERE + WE WRITING")
    cd = os.getcwd()
    file_name = cd + f"\\generated_video_code\\{file_name}"

    print(file_name)

    # Save the string as a .py file
    with open(file_name, "w", encoding="utf-8") as file:
        file.write(script)

    return f"File saved as filename {file_name}"





class makeTTSExplanation(BaseModel):
    script: str = Field(description="The explanation script you will use as a voiceover for the video you just made")
    output_file: str = Field(description="the file name for the .mp3 tts file. For the name, just do [thing your explaining].mp3. dont put the []")

@tool("make_tts_explanation", args_schema=makeTTSExplanation)
def make_tts_explanation(script: str, output_file: str):
    """Create the text to speech explanation file for your manim video. Only input your explanation script in text and the output file"""


    engine = pyttsx3.init()
    
    # Optional: Modify voice properties
    # engine.setProperty('rate', 150)    # Speed of speech
    # engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
    
    # Save to file

    audio_path = f"generated_audio\\{output_file}"
    engine.save_to_file(script, audio_path)
    engine.runAndWait()

    return f"audio file saved as {audio_path}"

class runScript(BaseModel):
    file_name: str = Field(description="The filename of the manim script you just made. It MUST be the same as the one used in WriteScript")
    script_class: str = Field(description="The main class of the script which contains the Scene.")
    audio_file: str = Field(description="The path to the audio file of the tts explanation you made")


@tool("run_script", args_schema=runScript)
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

    

TAVILY_TOOL = TavilySearchResults(max_results=10, tavily_api_key=os.environ['TAVILY_API_KEY'])

TOOLS = [TAVILY_TOOL,write_script, run_script, make_tts_explanation, handwrite_on_pdf]
