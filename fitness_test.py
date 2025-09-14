import os
import uuid
import subprocess
import numpy as np
from flask import Flask, render_template, request, jsonify, url_for
from werkzeug.utils import secure_filename

# import your push-up counter function
from pushup_counter import pushup_counter
from vertical_jump import detect_jumps_autoheight
from sit_ups import situp_counter
from sit_and_reach import sit_and_reach_tracker

app = Flask(__name__)

# folders
UPLOAD_FOLDER = os.path.join("static", "uploads")
OUTPUT_FOLDER = os.path.join("static", "outputs")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

ALLOWED_EXTS = {"mp4", "mov", "avi", "webm", "mkv"}

# ⚡ Full path to ffmpeg.exe (update if needed)
FFMPEG_PATH = r"C:\Users\Lenovo\Downloads\ffmpeg-7.1.1-full_build\bin\ffmpeg.exe"

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTS

def convert_webm_to_mp4(input_path, output_path):
    """
    Convert webm (or other input) to mp4 using ffmpeg if available.
    """
    cmd = [
        FFMPEG_PATH, "-y", "-i", input_path,
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        output_path
    ]
    try:
        subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def get_pushup_level(count, age, gender):
    """
    Determines the pushup fitness level based on age, gender, and count.
    """
    # Using the updated table for age ranges 14-17 and 20+
    if gender.lower() == 'male':
        if age >= 14 and age <= 17:
            if count >= 35:
                return "Excellent"
            elif count >= 18 and count <= 25:
                return "Average"
            else:
                return "Below Average"
        elif age >= 18 and age <= 19:
            if count >= 39:
                return "Excellent"
            elif count >= 22 and count <= 28:
                return "Average"
            else:
                return "Below Average"
        elif age >= 20:
            if count >= 30:
                return "Excellent"
            elif count >= 17 and count <= 21:
                return "Average"
            else:
                return "Below Average"
    elif gender.lower() == 'female':
        if age >= 14 and age <= 17:
            if count >= 28:
                return "Excellent"
            elif count >= 12 and count <= 18:
                return "Average"
            else:
                return "Below Average"
        elif age >= 18 and age <= 19:
            if count >= 33:
                return "Excellent"
            elif count >= 15 and count <= 20:
                return "Average"
            else:
                return "Below Average"
        elif age >= 20:
            if count >= 24:
                return "Excellent"
            elif count >= 12 and count <= 17:
                return "Average"
            else:
                return "Below Average"
    return "N/A" 


def get_jump_level(jump_height_cm, age, gender):
    """
    Determines the vertical jump fitness level based on age, gender, and jump height.
    """
    # Norms based on the provided image and common fitness standards
    jump_height_cm = float(jump_height_cm)
    if gender.lower() == 'male':
        if age >= 16 and age <= 19:
            if jump_height_cm >= 65:
                return "Excellent"
            elif jump_height_cm >= 50:
                return "Above Average"
            elif jump_height_cm >= 40:
                return "Average"
            elif jump_height_cm >= 30:
                return "Below Average"
            else:
                return "Poor"
        elif age >= 20:
            if jump_height_cm >= 70:
                return "Excellent"
            elif jump_height_cm >= 56:
                return "Above Average"
            elif jump_height_cm >= 41:
                return "Average"
            elif jump_height_cm >= 31:
                return "Below Average"
            else:
                return "Poor"
    elif gender.lower() == 'female':
        if age >= 16 and age <= 19:
            if jump_height_cm >= 58:
                return "Excellent"
            elif jump_height_cm >= 47:
                return "Above Average"
            elif jump_height_cm >= 36:
                return "Average"
            elif jump_height_cm >= 26:
                return "Below Average"
            else:
                return "Poor"
        elif age >= 20:
            if jump_height_cm >= 60:
                return "Excellent"
            elif jump_height_cm >= 46:
                return "Above Average"
            elif jump_height_cm >= 31:
                return "Average"
            elif jump_height_cm >= 21:
                return "Below Average"
            else:
                return "Poor"
    return "N/A"

def get_reach_level(reach_cm, age, gender):
    """
    Determines the sit-and-reach flexibility level based on age, gender, and reach in cm.
    """
    # Norms based on common fitness standards for younger adults
    reach_cm = float(reach_cm)
    if gender.lower() == 'male':
        if age >= 16 and age <= 19:
            if reach_cm >= 25: return "Excellent"
            elif reach_cm >= 20: return "Above Average"
            elif reach_cm >= 15: return "Average"
            else: return "Below Average"
        elif age >= 20 and age <= 30:
            if reach_cm >= 20: return "Excellent"
            elif reach_cm >= 15: return "Above Average"
            elif reach_cm >= 10: return "Average"
            else: return "Below Average"
    elif gender.lower() == 'female':
        if age >= 16 and age <= 19:
            if reach_cm >= 30: return "Excellent"
            elif reach_cm >= 25: return "Above Average"
            elif reach_cm >= 20: return "Average"
            else: return "Below Average"
        elif age >= 20 and age <= 30:
            if reach_cm >= 25: return "Excellent"
            elif reach_cm >= 20: return "Above Average"
            elif reach_cm >= 15: return "Average"
            else: return "Below Average"
    return "N/A"

def get_situp_level(count, age, gender):
    """
    Determines the sit-up fitness level based on age, gender, and count.
    Source: Norms from the President's Council on Physical Fitness and Sports
    """
    if gender.lower() == 'male':
        if age >= 16 and age <= 19:
            if count >= 45: return "Excellent"
            elif count >= 36: return "Above Average"
            elif count >= 29: return "Average"
            else: return "Below Average"
        elif age >= 20 and age <= 29:
            if count >= 49: return "Excellent"
            elif count >= 40: return "Above Average"
            elif count >= 34: return "Average"
            else: return "Below Average"
        elif age >= 30 and age <= 39:
            if count >= 41: return "Excellent"
            elif count >= 33: return "Above Average"
            elif count >= 27: return "Average"
            else: return "Below Average"
        else: return "N/A"
    elif gender.lower() == 'female':
        if age >= 16 and age <= 19:
            if count >= 42: return "Excellent"
            elif count >= 32: return "Above Average"
            elif count >= 25: return "Average"
            else: return "Below Average"
        elif age >= 20 and age <= 29:
            if count >= 44: return "Excellent"
            elif count >= 36: return "Above Average"
            elif count >= 28: return "Average"
            else: return "Below Average"
        elif age >= 30 and age <= 39:
            if count >= 38: return "Excellent"
            elif count >= 30: return "Above Average"
            elif count >= 24: return "Average"
            else: return "Below Average"
        else: return "N/A"
    return "N/A"



@app.route("/")
def index():
    return render_template("index.html")

# common  part so we have to make a fuunction with different name for all 4 fitness test 
@app.route("/upload", methods=["POST"])
def upload():
    if "video" not in request.files:
        return jsonify(error="No file part"), 400

    file = request.files["video"]
    age = request.form.get("age", type=int)
    gender = request.form.get("gender")

    if file.filename == "":
        return jsonify(error="No selected file"), 400

    if not all([age, gender]):
        return jsonify(error="Age and gender are required"), 400

    if not allowed_file(file.filename):
        return jsonify(error="File type not allowed"), 400

    # Save uploaded file with unique name
    filename = secure_filename(file.filename)
    unique_id = str(uuid.uuid4())[:8]
    input_filename = f"upload_{unique_id}_{filename}"
    input_path = os.path.join(UPLOAD_FOLDER, input_filename)
    file.save(input_path)

    # If uploaded webm (or non-mp4) convert to mp4 for OpenCV/MediaPipe reliability
    ext = filename.rsplit(".", 1)[1].lower()
    processing_input = input_path
    if ext != "mp4":
        converted_name = f"conv_{unique_id}.mp4"
        converted_path = os.path.join(UPLOAD_FOLDER, converted_name)
        ok = convert_webm_to_mp4(input_path, converted_path)
        if ok:
            processing_input = converted_path
        else:
            msg = (
                "Uploaded file is not MP4 and server conversion failed. "
                "Make sure ffmpeg path is correct."
            )
            return jsonify(error=msg), 500

    # Prepare output file path
    output_filename = f"processed_{unique_id}.mp4"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)

    # Run pushup counter
    try:
        pushup_count, produced_output_path = pushup_counter(processing_input, output_path)
    except Exception as e:
        return jsonify(error=f"Processing error: {e}"), 500

    # Determine fitness level
    pushup_level = get_pushup_level(pushup_count, age, gender)

    # Build the result URL with new parameters
    result_url = url_for("result", 
                         video=os.path.basename(produced_output_path), 
                         reps=pushup_count,
                         level=pushup_level)

    return jsonify(result_url=result_url)




@app.route("/result")
def result():
    video = request.args.get("video")
    reach = request.args.get("reach", "?")
    level = request.args.get("level", "N/A")
    if not video:
        return jsonify(error="Missing video"), 400

    video_url = url_for("static", filename=f"outputs/{video}")
    return render_template("result.html", video_url=video_url, max_reach=reach, reach_level=level)

if __name__ == "__main__":
    app.run(debug=True)