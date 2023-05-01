from flask import Flask, request, send_from_directory
import openai
import json
from jinja2 import Template
from tenacity import retry, wait_random_exponential, stop_after_attempt

# replace with your own openai key
with open("./openai.key") as f:
    openai.api_key = f.read().strip()

app = Flask(__name__)

# Uses jinja2 template to have different prompt for root path/homepage.
BASE_PROMPT = """{% if URL_PATH == "/" or URL_PATH == "" %}
Create a detailed response document with content that matches the following URL path: 
`{{URL_PATH}}`. First line: Content-Type. Then, response data. For HTML:
- Add related href links and "Back" buttons (href="../").
- Use simple inline CSS (Helvetica, margins).
- Set <title> as content summary.
- Include "More" link: href="/{{URL_PATH}}/more".
- Avoid duplicate paths/slashes in href.
If `{{URL_PATH}}` is / or blank, create "The Everything Website" with links to topics like:
- Science, Technology, History
- Arts, Philosophy, Health
- Travel, Sports, Entertainment
- Politics, Environment, Education
Include a message explaining the website, URL exploration,
 and source code link (https://github.com/bay40k/everything_website). 
 Mention users can input any URL for a new generated page.
{{OPTIONAL_DATA}}

Content-Type:
{% else %}
Create a detailed response document with content that matches the following URL path: 
`{{URL_PATH}}`. First line: Content-Type. Then, response data. For HTML:
- Add related href links and "Back" buttons (href="../").
- Use simple inline CSS (Helvetica, margins).
- Set <title> as content summary.
- Include "More" link: href="/{{URL_PATH}}/more".
- Avoid duplicate paths/slashes in href.
- Text content should be around at least a few paragraphs, or more.
{{OPTIONAL_DATA}}

Content-Type:
{% endif %}
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


@app.route("/api/", methods=["GET"])
@app.route("/api/<path:path>", methods=["GET"])
def catch_all(path=""):
    template = Template(BASE_PROMPT)
    if request.form:
        prompt = template.render(
            URL_PATH=path, OPTIONAL_DATA=f"form data: {json.dumps(request.form)}"
        )
    else:
        prompt = template.render(URL_PATH=path, OPTIONAL_DATA="")

    response = completion_with_backoff(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0.7,
        max_tokens=512,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    ai_data = response.choices[0].text

    print(ai_data)

    content_type = ai_data.splitlines()[0]
    response_data = "\n".join(ai_data.splitlines()[1:])
    return response_data, 200, {"Content-Type": content_type}


def main():
    app.run(host="0.0.0.0", port=8080, debug=True)


if __name__ == "__main__":
    main()
