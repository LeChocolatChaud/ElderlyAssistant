import zhipuai
import requests
import json
import base64
import wave
import pydub
from io import BytesIO
from aip import AipSpeech

baidu_keys = {}
def set_bd_keys(keys):
    global baidu_keys
    baidu_keys = keys
BOTS = {}

class Bot:
    def __init__(self):
        with open("background.txt", "r", encoding="utf-8") as f:
            background_text = f.read()
        response = zhipuai.model_api.sse_invoke(
            model="chatglm_lite",
            prompt=[{"role": "user", "content": background_text}],
            temperature=0.9,
        )
        response_text = ""
        for event in response.events():
            response_text += event.data
        self.session = [
            {"role": "user", "content": background_text},
            {"role": "assistant", "content": response_text}
        ]
        self.aip_client = AipSpeech(appId=baidu_keys["app_id"], apiKey=baidu_keys["api_key"], secretKey=baidu_keys["secret_key"])

    def chat(self, message: str) -> str:
        self.session.append({"role": "user", "content": message})
        response = zhipuai.model_api.sse_invoke(
            model="chatglm_lite",
            prompt=self.session,
            temperature=0.9,
        )
        response_text = ""
        for event in response.events():
            response_text += event.data
        self.session.append({"role": "assistant", "content": response_text})
        return response_text
    
    def speech_to_text(self, file_data: bytes) -> str:
        audio = pydub.AudioSegment(data=file_data)
        audio = audio.set_channels(1)
        audio = audio.set_frame_rate(16000)
        audio_io = BytesIO()
        audio.export(audio_io, format="wav")
        audio_data = audio_io.getvalue()
        response = self.aip_client.asr(speech=audio_data, format="wav", rate=audio.frame_rate, options={"cuid": baidu_keys["cuid"]})
        if "result" not in response:
            return ""
        return response["result"][0]
