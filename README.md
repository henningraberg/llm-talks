# LLM Talks
[![Code style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff) 
[![Python 3.9](https://img.shields.io/badge/python-3.9-gree.svg)](https://www.python.org/downloads/release/python-390/)
[![Python 3.10](https://img.shields.io/badge/python-3.10-gree.svg)](https://www.python.org/downloads/release/python-3100/)
[![Python 3.11](https://img.shields.io/badge/python-3.11-gree.svg)](https://www.python.org/downloads/release/python-3110/)
[![Python 3.12](https://img.shields.io/badge/python-3.12-gree.svg)](https://www.python.org/downloads/release/python-3120/)
[![Python 3.13](https://img.shields.io/badge/python-3.13-gree.svg)](https://www.python.org/downloads/release/python-3130/)

A CLI tools for running an interactive conversation between two LLM models.

## Installation
1. Clone the repository
```bash
git clone https://github.com/henningraberg/llm-talks.git
```

2. Navigate to the cloned directory
```bash
cd llm-talks
```

3. Set up docker containers, python environment and packages (make sure you have Docker running)
```bash
make install
```

4. Activate the python environment
```bash
source venv/bin/activate
```

5. Download the models you want to use (brows available models here &#8594; https://ollama.com/library)
```bash
python llm-talks.py download-model <model_name>
```

6. Set up a conversation
```bash
python llm-talks.py set-up-conversation
```

7. Run conversation
```bash
python llm-talks.py run-conversation --conv_id <conversation id>
```

## Usage
```
Usage: llm-talks.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  build-db             Create the database.
  download-model       Download LLM model.
  list-conversations   List conversations.
  list-models          List all downloaded models.
  nuke-db              Clean the database.
  remove-conversation  Remove conversation.
  remove-model         Remove model.
  run-conversation     Run the given conversation.
  set-up-conversation  Set up a conversation.
  show-conversation    Prints the given conversation.
  show-model           Get model information.
```