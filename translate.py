from dotenv import load_dotenv
from google import genai
from google.genai import types

def unpack_text_and_bbox(result: list):
    placeholder = [(bbox, text) for bbox, text, _ in result]
    bbox_list = list(map(lambda x: x[0], placeholder))
    text_to_translate = list(map(lambda x: x[1], placeholder))
    return bbox_list, text_to_translate

def process_text_for_api(text_to_translate : list):
    text_for_translation = '\n'.join(text_to_translate)
    return text_for_translation

def translate_text(result: list, client) -> list[tuple] | None:
    bbox, preproccessed_text = unpack_text_and_bbox(result)
    text = process_text_for_api(preproccessed_text)
    
    response = client.models.generate_content(
        model = "gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction="Translate the following Japanese text into natural English while keeping the nuances of native Japanese. Do not add explanations, notes, interpretations, or context. If the text is ambiguous, translate it literally and directly. Output only the translation and nothing else."
        ),
        contents = text
    )
    translated_text = response.text.split('\n')

    try:
        return [(box, string) for box, string in zip(bbox, translated_text)]
    except Exception:
        return None
    

