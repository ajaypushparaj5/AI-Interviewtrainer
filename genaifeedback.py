# from google import genai
# import os
# from dotenv import load_dotenv

# load_dotenv()
# client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# def genairesponse(report):
#     print("API Key",os.getenv("GEMINI_API_KEY"))
#     resp = client.models.generate_content(
#         model="gemini-2.0-flash",
#         contents=f"""
# You are a professional body language coach. 
# I will give you an analysis dictionary of someone's presentation. 
# Your job is to turn the numbers into clear, friendly feedback.

# Here is the analysis data:
# {report}

# Please:
# 1. Summarize overall performance (1 short paragraph).
# 2. Highlight strengths.
# 3. Give 3-4 specific improvement tips.
# 4. Keep it encouraging, not robotic.
# """

#     )

#     return resp.text




# from huggingface_hub import InferenceClient
# import os
# from dotenv import load_dotenv

# load_dotenv()

# client = InferenceClient(
#     model="HuggingFaceH4/zephyr-7b-beta",
#     token=os.getenv("HF_API_TOKEN"),
#     provider="hf-inference"
# )

# # def genairesponse(report):
# #     prompt = f"""
# # You are a professional body language coach.

# # I will give you an analysis dictionary of someone's presentation.
# # Your job is to turn the numbers into clear, friendly feedback.

# # Here is the analysis data:
# # {report}

# # Please:
# # 1. Summarize overall performance (1 short paragraph).
# # 2. Highlight strengths.
# # 3. Give 3-4 specific improvement tips.
# # 4. Keep it encouraging, not robotic.
# # """

# #     response = client.text_generation(
# #         prompt,
# #         max_new_tokens=350,
# #         temperature=0.7,
# #         top_p=0.9
# #     )

# #     return response
# def genairesponse(report):
#     # Format as a list of messages
#     messages = [
#         {"role": "system", "content": "You are a professional body language coach."},
#         {"role": "user", "content": f"Turn this analysis data into friendly feedback:\n{report}"}
#     ]

#     # Use chat_completion instead of text_generation
#     response = client.chat_completion(
#         messages=messages,
#         max_tokens=500,
#         temperature=0.7     
#     )

#     return response.choices[0].message.content

import os
import requests
import json

def genairesponse(report):
    # We will use the Qwen model via a local Ollama instance
    model_id = "qwen2.5:7b" 
    url = "http://localhost:11434/api/chat"
    
    messages = [
        {
            "role": "system", 
            "content": "You are a professional body language coach. Turn numerical data into friendly, helpful presentation feedback. Highlight strengths and suggest 3-4 specific improvement tips."
        },
        {
            "role": "user", 
            "content": f"Analyze this body language data: {report}"
        }
    ]

    payload = {
        "model": model_id,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0.7
        }
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()["message"]["content"]
    except requests.exceptions.ConnectionError:
        return "Coaching Error: Could not connect to local LLM. Please make sure Ollama is installed, running locally, and the Qwen model is downloaded (run `ollama run qwen2.5`)."
    except Exception as e:
        return f"Coaching Error: {str(e)}"

