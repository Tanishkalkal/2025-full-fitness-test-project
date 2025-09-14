import os
import uuid
import subprocess
from flask import Flask, render_template, request, jsonify, url_for
from werkzeug.utils import secure_filename

# import your push-up counter function
from pushup_counter import pushup_counter

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
    return "N/A" # Default if no category matches
# common  part so we have to make a fuunction with different name for all 4 fitness test 
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
    reps = request.args.get("reps", "?")
    level = request.args.get("level", "N/A")
    if not video:
        return jsonify(error="Missing video"), 400

    # static file path: static/outputs/<video>
    video_url = url_for("static", filename=f"outputs/{video}")
    return render_template("result.html", pushup_count=reps, pushup_level=level)

if __name__ == "__main__":
    app.run(debug=True)
