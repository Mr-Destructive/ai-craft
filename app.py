import io
import os

import aiohttp
from dotenv import load_dotenv
#from PIL import Image
import requests
#from rembg import remove

load_dotenv()

from fastapi import FastAPI, Form, Request, Response, Query, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles


app = FastAPI()
app.mount("/static", StaticFiles(directory="static/"), name="static")
templates = Jinja2Templates(directory="templates/")

API_KEYS = "I AM NOT GOING TO SHOW MY KEYS"
API_KEYS = os.environ.get("COHERE_API_KEYS")

OPENAI_URL = "https://api.openai.com/v1/"
COHERE_URL = "https://api.cohere.ai/v1/"

@app.get("/")
async def root(request: Request):
    api_endpoints = ['/chat', '/youtube-url']
    return templates.TemplateResponse('index.html', context={'request': request, 'result': api_endpoints})

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
async def chat_get(request: Request, q: str = Query(None, min_length=10)):
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
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{COHERE_URL}generate", headers=headers, json=data) as response:
                response = await response.json()
        #response = requests.post(f"{COHERE_URL}generate", headers=headers, json=data)
        if response.status_code != 200:
            return "500: Invernal Server Error"
        result = "<br><b>User: </b>" + q + "<br><br>"
        result += "<b>AI: </b>" + str(response.json().get("generations")[0]["text"]).replace("\n", "<br>")
    else:
        result = "Type a question"
    return templates.TemplateResponse('chat.html', context={'request': request, 'result': result})


@app.post("/chat")
async def chat_post(request: Request,  msg: str= Form(...)):
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
    #response = requests.post(f"{COHERE_URL}generate", headers=headers, json=data)
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{COHERE_URL}generate", headers=headers, json=data) as response:
            response = await response.json()
            if not response.get('generations'):
                return "<h2>500: Invernal Server Error</h2>"
            result = "<br><b>User: </b>" + msg + "<br><br>"
            result += "<b>AI: </b>" + str(response.get("generations")[0]["text"]).replace("\n", "<br>")
            return result

@app.get("/youtube-url")
async def video_url(request: Request, q: str = Query(None, min_length=10)):
    result = "Enter a youtube video URL"
    return templates.TemplateResponse('youtube.html', context={'request': request, 'result': result})

@app.post("/youtube-url")
async def get_video_from_url(request: Request, msg: str = Form(...)):
    folder = "static/videos"
    if not os.path.exists(folder):
        os.makedirs(folder)

    import pytube
    url = msg
    yt = pytube.YouTube(url)
    stream = yt.streams.get_highest_resolution()
    video = stream.download(output_path=folder)

    video_filename = os.path.basename(video)
    rendered_video = os.path.join(folder, video_filename)

    return templates.TemplateResponse("youtube_render.html", media_type="video/mp4", context={'request': request, 'url': rendered_video})


@app.get('/pics')
async def get_pics(request: Request):
    space_id = "my-space"
    model_id = "dalle-mini"

    url = "https://huggingface.co/spaces/dalle-mini/generate"
    params = {
        "space_id": space_id,
        "model_id": model_id,
        "prompt": "A cat sitting on a chair"
    }
    response = requests.post(url, params=params)
    image = response.content
    print(image)
    return templates.TemplateResponse('pics.html', context={'request': request, 'result': image})

#@app.get("/pics")
#def pics_get(request: Request):
#    result = "Enter the prompt"
#    return templates.TemplateResponse('pics.html', context={'request': request, 'result': result})
#
#
#@app.post("/pics")
#def pics_post(request: Request, msg: str= Form(...)):
#    headers = {
#        "Content-Type": "application/json",
#        "Authorization": f"Bearer {API_KEYS}"
#    }
#    data = {
#        "prompt": msg,
#        "n": 5,
#        "size": "256x256"
#    }
#    response = requests.post(f"{COHERE_URL}images/generations", headers=headers, json=data)
#    result = "<br><b>User: </b>" + msg + "<br><br>"
#    for image in response.json().get("data"):
#        result += f"<img src=\'{image.get('url')}\'>"
#    return result
#
#
#@app.get("/rmbg")
#async def rmbg_form(request: Request):
#    return templates.TemplateResponse('rmbg.html', context={'request': request})
#
#
#@app.post("/rmbg")
#async def rmbg_img(request: Request, image: UploadFile = File(...)):
#    img = Image.open(io.BytesIO(await image.read()))
#    output = remove(img)
#    if not img.filename:
#        filename = 'temp'
#    else:
#        filename = img.filename
#    output_file_path = "output/imgs/" + filename + '.png'
#    output.save(output_file_path)
#    return templates.TemplateResponse('rmbg_img.html', context={'request': request,'img_url': output_file_path})
