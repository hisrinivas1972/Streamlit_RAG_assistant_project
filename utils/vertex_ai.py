import requests
import json

def generate_answer_google_api(prompt, api_key):
    url = "https://generativelanguage.googleapis.com/v1beta/models/text-bison-001:generateText"
    params = {"key": api_key}
    payload = {"prompt": prompt}
    r = requests.post(url, params=params, json=payload)
    if r.ok:
        return r.json()["candidates"][0]["output"]
    return f"Error: {r.text}"
