import openai
import os
import logging
 
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI, OpenAIError
from slowapi import Limiter
from slowapi.util import get_remote_address

app = FastAPI()

# Allow frontend to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://resume-chatbot-frontend-hristijanqas-projects.vercel.app"],  # Change this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Your resume data
resume_data = {
    "name": "Hristijan Ivanovski",
    "title": "QA Engineer & Automation Specialist",
    "experience": "5+ years in Software Testing & QA",
    "skills": ["Selenium", "Python", "JavaScript", "Salesforce QA", "Jira Automation"],
    "projects": [
        {"name": "Jira-Jenkins Integration", "description": "Automated CI/CD pipeline trigger"},
        {"name": "Resume Chatbot", "description": "AI-based chatbot for HR inquiries"}
    ]
}

# OpenAI API Key (replace with your actual key)

@app.get("/")
def read_root():
    return {"message": "Hello, this is the backend!"}

@app.get("/resume")
def get_resume():
    return resume_data

@app.post("/chat")
@limiter.limit("5/minute")  # 5 requests per minute per user
def chat_with_ai(request: dict):
    try:
        # Check if "text" key exists in request
        user_question = request.get("text")
        if not user_question:
            raise HTTPException(status_code=400, detail="The 'text' field is required.")

        # Build the prompt
        prompt = f"Based on this resume data: {resume_data}\nHR asked: {user_question}\nAnswer: "

        # Call OpenAI API
        client = OpenAI(api_key="OPENAI_API_KEY")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant answering HR-related questions about a resume."},
                {"role": "user", "content": prompt}
            ]
        )

        # Extract and return the AI response
        ai_response = response.choices[0].message.content
        return {"response": ai_response}

    except KeyError:
        logger.error("Missing 'text' key in request")
        raise HTTPException(status_code=400, detail="Invalid request format. Expected JSON with 'text' key.")
    
    except OpenAIError as e:
        logger.error(f"OpenAI API error: {e}")
        raise HTTPException(status_code=502, detail="Error communicating with AI service. Please try again later.")

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error. Please contact support.")
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)