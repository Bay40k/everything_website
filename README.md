# The Everything Website

This is a web application that generates a dynamic response based on the provided URL path. It uses the OpenAI GPT-4 model to create the content.

## Getting Started

### Prerequisites

- Python 3.6 or higher and pip
- flask
- openai
- waitress
- tenacity
- virtualenv (optional)

### Installation

1. Clone the repository:
    ```
    git clone https://github.com/bay40k/everything_website
    cd everything_website
    ```

2. Create a virtual environment (optional):
    ```
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Install the dependencies:
    ```
    pip install -r requirements.txt
    ```

4. Replace the API key file with your own OpenAI key:
    ```
    echo "your_openai_key" > openai.key
    ```

### Running the application

To run the application locally, execute the following command:
```
python run.py
```

Now you can access the application at `http://localhost:5000` in your web browser.

## Acknowledgements

A big chunk of the code, and the idea, is borrowed from: [LiveOverflow/everything-api](https://github.com/LiveOverflow/everything-api).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
