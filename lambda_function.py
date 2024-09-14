import base64
from doctest import master
import json
import openai
import re
import time

openai.api_key = "<INSERT OPENAI API KEY HERE>"

masterprompt = [
    {
        "role": "system",
        "content": "You are an ai phone assistant called Julie. people, usually older folks, will call you and ask questions.",
    },
    {
        "role": "system",
        "content": "Do not make assumptions - if you don't know say you aren't sure. Be concise and to the point.",
    },
    {
        "role": "system",
        "content": "Your response will be read aloud - give full paragraph responses and do not add any numbering or formatting.",
    },
]


def lambda_handler(event, context):
    start_x = time.time()
    # key = event.get('key')
    # if key != '<SERVER SIDE AUTH KEY HERE>': # TODO: re-enable auther, it's broken on the twilio end
    #     print('Unauthorized')
    #     return {
    #         'statusCode': 401,
    #         'body': 'Unauthorized'
    #     }
    text = event.get("text") or ""
    history = event.get("history") or "W10="
    phone = event.get("phone") or False
    max_execution = event.get("max_execution") or 4
    raw = event.get("raw") or False
    if not raw:
        text = text + " Please keep your response brief."

    history = json.loads(base64.b64decode(history).decode("utf-8"))

    messages = (
        masterprompt
        + history
        + [
            {
                "role": "user",
                "content": text,
            },
        ]
    )

    streams = []
    message = ""
    for completion in openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=messages,
        stream=True,
    ):
        content = completion["choices"][0]["delta"].get("content", "")
        if content:
            message += content
        streams.append(completion)
        elapsed = time.time() - start_x
        if phone and elapsed > max_execution:
            break

    if phone:
        trunc_match = re.search(r"(.*)[\.!\?]", message)
        if trunc_match is not None:
            message = trunc_match[0]
    history = history + [
        {
            "role": "user",
            "content": text,
        },
        {
            "role": "assistant",
            "content": message,
        },
    ]

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "elapsed": time.time() - start_x,
                "message": message,
                "phone": phone,
                "history": str(
                    base64.b64encode(
                        bytes(
                            json.dumps(history),
                            "utf-8",
                        )
                    ).decode("ascii")
                ),
            }
        ),
    }
