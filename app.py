from flask import Flask, request, send_from_directory
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
In case of a html response:
- add relative href links to related topics.
- add relative href "Back" buttons to the previous page, like: href="../"
- add inline css style to the html document; Use mild formatting like Helvetica font, margins, etc. Try to keep the style simple, visually centered and easy to read.
- set <title> to a summary of the content.
- add a more content link to the bottom of the page, like: href="{{URL_PATH}}/more"
- Remove duplicate paths/slashes in href links; Example: href="/about/tech" is good, href="//about/about///tech/" is bad.
If {{URL_PATH}} is /, then the response document is a website called "The Everything Website", which contains various links to any kind of topics.
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


@app.route("/", methods=["GET"])
@app.route("/<path:path>", methods=["GET"])
def serve_index(path=""):
    return send_from_directory(".", "index.html")


# @app.route("/api", methods=["GET"])
@app.route("/api/", methods=["GET"])  # Add this line
@app.route("/api/<path:path>", methods=["GET"])
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
