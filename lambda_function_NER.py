import base64
from doctest import master
import json
import openai
import re
import time

openai.api_key = "<INSERT OPENAI API KEY HERE>"

ner_labels = (
    [  # https://cookbook.openai.com/examples/named_entity_recognition_to_enrich_text
        "person",  # people, including fictional characters
        "fac",  # buildings, airports, highways, bridges
        "org",  # organizations, companies, agencies, institutions
        "gpe",  # geopolitical entities like countries, cities, states
        "loc",  # non-gpe locations
        "product",  # vehicles, foods, appareal, appliances, software, toys
        "event",  # named sports, scientific milestones, historical events
        "work_of_art",  # titles of books, songs, movies
        "law",  # named laws, acts, or legislations
        "language",  # any named language
        "date",  # absolute or relative dates or periods
        "time",  # time units smaller than a day
        "percent",  # percentage (e.g., "twenty percent", "18%")
        "money",  # monetary values, including unit
        "quantity",  # measurements, e.g., weight or distance
    ]
)

masterprompt = [
    {
        "role": "system",
        "content": "You are an ai phone assistant called Julie. people, usually older folks, will call you and ask questions.",
    },
    {
        "role": "system",
        "content": "Do not make assumptions - if you don't know say you aren't sure.",
    },
    {
        "role": "system",
        "content": "Your response will be read aloud - give full paragraph responses and do not add any numbering or formatting.",
    },
    {
        "role": "system",
        "content": f"""
You are an expert in Natural Language Processing. Your task is to identify common Named Entities (NER) in a given text.
The possible common Named Entities (NER) types are exclusively: ({", ".join(ner_labels)}).""",
    },
]

ner_oneshot = [
    {
        "role": "assistant",
        "content": f"""
            EXAMPLE:
                Text: 'I have an appointment with Dr. Smith on 12/12/2022. I will be in Germany for 3 days. and will be back on 12/15/2022. I'm having surgery on my knee and will be receiving a synthetic knee replacement. This will cost me $10,000, of which $8,000 will be covered by insurance.'
                {{
                    "person": ["Dr. Smith"],
                    "date": ["12/12/2022", "12/15/2022"],
                    "gpe": ["Germany"],
                    "quantity": ["3 days", "$10,000", "$8,000"],
                }}
            --""",
    }
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
    history = event.get("history") or "W10="  # TODO: remove this default history
    phone = event.get("phone") or False
    max_execution = event.get("max_execution") or 4
    raw = event.get("raw") or False
    if not raw:
        text = text + " Please keep your response brief."

    history = json.loads(base64.b64decode(history).decode("utf-8"))

    messages = (
        masterprompt
        + ner_oneshot
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
