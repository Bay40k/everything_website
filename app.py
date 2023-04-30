from flask import Flask, request
import os
import openai
import json

from tenacity import retry, wait_random_exponential, stop_after_attempt

# replace with your own openai key
with open("./openai.key") as f:
    openai.api_key = f.read().strip()

app = Flask(__name__)

BASE_PROMPT = """Create a response document with content that matches the following URL path: 
    `{{URL_PATH}}`

The first line is the Content-Type of the response.
The following lines is the returned data.
In case of a html response, add relative href links with to related topics.
{{OPTIONAL_DATA}}

Content-Type:
"""

MAX_RETRIES = 12
MIN_RETRY_TIME = 1
MAX_RETRY_TIME = 8


@retry(
    wait=wait_random_exponential(min=MIN_RETRY_TIME, max=MAX_RETRY_TIME),
    stop=stop_after_attempt(MAX_RETRIES),
    reraise=True,
)
def completion_with_backoff(**kwargs):
    return openai.Completion.create(**kwargs)


@app.route("/", methods=["POST", "GET"])
@app.route("/<path:path>", methods=["POST", "GET"])
def catch_all(path=""):

    if request.form:
        prompt = BASE_PROMPT.replace(
            "{{OPTIONAL_DATA}}", f"form data: {json.dumps(request.form)}"
        )
    else:
        prompt = BASE_PROMPT.replace("{{OPTIONAL_DATA}}", f"")

    prompt = prompt.replace("{{URL_PATH}}", path)

    response = completion_with_backoff(
        # response = openai.ChatCompletion.create(
        model="text-davinci-003",
        prompt=prompt,
        # model="gpt-4",
        # messages=[{"role": "system", "content": prompt}],
        temperature=0.7,
        max_tokens=512,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    ai_data = response.choices[0].text
    # ai_data = response["choices"][0]["message"]["content"].strip()

    print(ai_data)

    content_type = ai_data.splitlines()[0]
    response_data = "\n".join(ai_data.splitlines()[1:])
    return response_data, 200, {"Content-Type": content_type}


def main():
    app.run(host="0.0.0.0", port=8080, debug=True)


if __name__ == "__main__":
    main()
