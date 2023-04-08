import requests
import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Form, Request, Query 
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates/")

API_KEYS = "I AM NOT GOING TO SHOW MY KEYS"
API_KEYS = os.environ.get("COHERE_API_KEYS")

OPENAI_URL = "https://api.openai.com/v1/"
COHERE_URL = "https://api.cohere.ai/v1/"

@app.post("/api")
async def chat(prompt: dict):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEYS}"
    }
    data = {
        "prompt": prompt["msg"],
        "model": "code-davinci-003",
        "max_tokens": 800,
        "temperature": 0.7,
    }
    response = requests.post(f"{COHERE_URL}generate", headers=headers, json=data)
    return (response.json())


@app.get("/chat")
def chat_get(request: Request, q: str = Query(None, min_length=10)):
    if q:
        data = {
            "prompt": q,
            "model": "command-xlarge-nightly",
            "max_tokens": 800,
            "temperature": 0.7,
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEYS}"
        }
        response = requests.post(f"{COHERE_URL}generate", headers=headers, json=data)
        if response.status_code != 200:
            return "500: Invernal Server Error"
        result = "<br><b>User: </b>" + q + "<br><br>"
        result += "<b>AI: </b>" + str(response.json().get("generations")[0]["text"]).replace("\n", "<br>")
    else:
        result = "Type a question"
    return templates.TemplateResponse('index.html', context={'request': request, 'result': result})


@app.post("/chat")
def chat_post(request: Request,  msg: str= Form(...)):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEYS}"
    }

    data = {
        "prompt": msg,
        "model": "command-xlarge-nightly",
        "max_tokens": 800,
        "temperature": 0.7,
    }
    response = requests.post(f"{COHERE_URL}generate", headers=headers, json=data)
    if response.status_code != 200:
        return "<h2>500: Invernal Server Error</h2>"
    result = "<br><b>User: </b>" + msg + "<br><br>"
    result += "<b>AI: </b>" + str(response.json().get("generations")[0]["text"]).replace("\n", "<br>")
    return result

@app.get("/pics")
def pics_get(request: Request):
    result = "Enter the prompt"
    return templates.TemplateResponse('pics.html', context={'request': request, 'result': result})


@app.post("/pics")
def pics_post(request: Request, msg: str= Form(...)):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEYS}"
    }
    data = {
        "prompt": msg,
        "n": 5,
        "size": "256x256"
    }
    response = requests.post(f"{COHERE_URL}images/generations", headers=headers, json=data)
    result = "<br><b>User: </b>" + msg + "<br><br>"
    for image in response.json().get("data"):
        result += f"<img src=\'{image.get('url')}\'>"
    return result
