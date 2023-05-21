import uuid
from typing import Optional

import requests


def longevity_gpt(question: str, history: list[str],
                  is_new_topic: bool = True,
                  session_id: Optional[str] = None):
    url = 'http://asklongevitygpt.com/answer'
    headers = {'Content-Type': 'application/json'} # We want to send JSON data
    if session_id is None:
        session_id = str(uuid.uuid4())
    # This will be the JSON body of the POST request

    data = {
        'question': question,
        'conversation_history': history,
        'is_new_topic': is_new_topic,
        'session_id': session_id,
        "gpt_version" : "gpt-4"
    }
    response: requests.Response = requests.post(url, headers=headers, json=data)
    result = response.json()
    print(f"RESPONSE WAS: {result['answer']}")
    return response