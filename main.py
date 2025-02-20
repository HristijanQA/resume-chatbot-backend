import openai
import os
import uvicorn 
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI

app = FastAPI()

# Allow frontend to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://resume-chatbot-frontend-hristijanqas-projects.vercel.app"],  # Change this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

def chat_with_ai(question: dict):
    
    try:
        prompt = f"Based on this resume data: {resume_data}\nHR asked: {question['text']}\nAnswer: "
        client = OpenAI(api_key="OPENAI_API_KEY")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are a helpful assistant answering HR-related questions about a resume."},
                      {"role": "user", "content": prompt}]
        )

        return {"response": response['choices'][0]['message']['content']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Railway uses PORT, default to 8000
    uvicorn.run("main:app", host="0.0.0.0", port=port)  # ✅ Correct for FastAPI