from fastapi import FastAPI, Form, Request
from fastapi.templating import Jinja2Templates
import requests

app = FastAPI()
templates = Jinja2Templates(directory="templates/")
API_KEYS = "I AM NOT GOING TO SHOW MY KEYS"


@app.post("/api")
async def chat(prompt: dict):
    openai_url = "https://api.openai.com/v1/completions"
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
    response = requests.post(openai_url, headers=headers, json=data)
    return (response.json())


@app.get("/chat")
def chat_get(request: Request):
    result = "Type a question"
    return templates.TemplateResponse('index.html', context={'request': request, 'result': result})


@app.post("/chat")
def chat_post(request: Request, msg: str= Form(...)):
    openai_url = "https://api.openai.com/v1/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEYS}"
    }
    data = {
        "prompt": msg,
        "model": "text-davinci-003",
        "max_tokens": 800,
        "temperature": 0.7,
    }
    response = requests.post(openai_url, headers=headers, json=data)
    result = "<br><b>User: </b>" + msg + "<br><br>"
    result += "<b>AI: </b>" + str(response.json().get("choices")[0]["text"]).replace("\n", "<br>")
    return result

@app.get("/pics")
def pics_get(request: Request):
    result = "Enter the prompt"
    return templates.TemplateResponse('pics.html', context={'request': request, 'result': result})


@app.post("/pics")
def pics_post(request: Request, msg: str= Form(...)):
    openai_url = "https://api.openai.com/v1/images/generations"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEYS}"
    }
    data = {
        "prompt": msg,
        "n": 5,
        "size": "256x256"
    }
    response = requests.post(openai_url, headers=headers, json=data)
    result = "<br><b>User: </b>" + msg + "<br><br>"
    for image in response.json().get("data"):
        result += f"<img src=\'{image.get('url')}\'>"
    return result
