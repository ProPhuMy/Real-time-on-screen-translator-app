import requests
import json
import screenshot as sc
from dotenv import load_dotenv
import os

load_dotenv()
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')

def unpack_text_and_bbox(result: list):
    placeholder = [(bbox, text) for bbox, text, _ in result]
    bbox_list = list(map(lambda x: x[0], placeholder))
    text_to_translate = list(map(lambda x: x[1], placeholder))
    return bbox_list, text_to_translate

def process_text_for_api(text_to_translate : list):
    text_for_translation = '\n'.join(text_to_translate)
    return text_for_translation

def translate_text(result: list):
    bbox, preproccessed_text = unpack_text_and_bbox(result)
    text = process_text_for_api(preproccessed_text)

    url="https://openrouter.ai/api/v1/chat/completions"
    headers={
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json"
  }

    data={
    "model": "cognitivecomputations/dolphin-mistral-24b-venice-edition:free", 
    "messages": [
      {
        "role": "user",
        "content": f"Translate this Japanese text to English. Provide only the translation, no explanations:\n\n{text}"
      }
    ]
  }
    
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        result = response.json()
        translated_text = result['choices'][0]['message']['content']
        translated_text = translated_text.split()
    else:
        print('failed to get response from api')
    return [(box, string) for box, string in zip(bbox, translated_text)]
