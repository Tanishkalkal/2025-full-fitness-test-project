import os
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS

# Initialize Flask App
app = Flask(__name__)
CORS(app) 

# --- Configure the Google Gemini API Key ---
# Best Practice: Set this as an environment variable
try:
    api_key = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=api_key)
except Exception as e:
    # Fallback for easy testing: add key directly
    # genai.configure(api_key="YOUR_GOOGLE_API_KEY_HERE")
    print("Warning: GOOGLE_API_KEY environment variable not set.")


# --- YOUR CUSTOM WEBSITE CONTEXT GOES HERE ---
# In your main.py file, replace the old WEBSITE_CONTEXT with this new one:

WEBSITE_CONTEXT = """
You are a helpful and versatile AI assistant for a website called 'SAI Sports Analyzer'.
Your primary role is to be an expert on the website. If a user's question is about the website, use the detailed information below to give a specific and accurate answer.
For all other general questions (like asking for YouTube links, explaining topics, or having a conversation), you should act as a general knowledgeable assistant and answer helpfully.

Here is the detailed information about the SAI Sports Analyzer website:
- **Name**: SAI Sports Analyzer
- **Purpose**: To help athletes and coaches unlock their athletic potential using data-driven insights from video analysis.
- **How it Works**: Users upload performance videos for specific fitness tests. The platform analyzes the videos to provide objective, measurable data.

- **Key Features**:
  - **Objective Analysis**: Provides precise metrics on speed, power, and agility to eliminate guesswork.
  - **Performance Tracking**: Users can track their progress over time with graphs and score histories for each test.
  - **Leaderboards**: Athletes can compare their results against others at the district, state, and national levels.
  - **Daily Streaks**: A feature to motivate users to perform tests consistently.
  - **My Training Goals**: A section where users can add and track their daily and overall training goals.
  - **AI-Powered Feedback**: After a test evaluation, users can get feedback and improvement tips from an AI Coach.
  - **Performance Analysis**: A radar chart that shows a user's overall athletic profile against national benchmarks.

- **Available Fitness Tests**:
  - **General Fitness**: Sit Ups, Push Ups, Vertical Height Jump, and Sit and Reach Test.
  - **Game-Specific**: There are also specialized tests for Football, Cricket, Hockey, Badminton, and Athletics.

- **Other Website Sections**:
  - **Upcoming Events**: A carousel shows major upcoming sporting events like the Olympics and Khelo India Youth Games.
  - **Testimonials**: Features positive reviews from coaches and athletes.
  - **User Accounts**: Users can sign up, log in, and view their personal profile with details like age, height, weight, and BMI.
"""

# This function calls the Gemini API
def get_ai_response(prompt):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        
        # Combine your instructions with the user's question
        full_prompt = f"{WEBSITE_CONTEXT}\n\nUser Question: {prompt}"
        
        response = model.generate_content(full_prompt)
        return response.text.strip()
    except Exception as e:
        print(f"An error occurred with the Gemini API: {e}")
        return "Sorry, I'm having trouble connecting to the AI service right now."

# This is the API endpoint your website will call
@app.route('/chat', methods=['POST'])
def handle_chat():
    data = request.json
    user_prompt = data.get('prompt')

    if not user_prompt:
        return jsonify({"error": "No prompt provided"}), 400

    bot_response = get_ai_response(user_prompt)
    return jsonify({"response": bot_response})

# Run the server
if __name__ == "__main__":
    app.run(port=5000, debug=True)
    
    
    
    
    # AIzaSyAwfQhYUt2yEe44CEGofpskXY-MF1DaxsQ      $env:GOOGLE_API_KEY="AIzaSyAwfQhYUt2yEe44CEGofpskXY-MF1DaxsQ"