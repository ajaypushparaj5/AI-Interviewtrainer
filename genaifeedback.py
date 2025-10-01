from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def genairesponse(report):
    resp = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=f"""
You are a professional body language coach. 
I will give you an analysis dictionary of someone's presentation. 
Your job is to turn the numbers into clear, friendly feedback.

Here is the analysis data:
{report}

Please:
1. Summarize overall performance (1 short paragraph).
2. Highlight strengths.
3. Give 3-4 specific improvement tips.
4. Keep it encouraging, not robotic.
"""

    )
    return resp.text
