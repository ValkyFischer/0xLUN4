# Luna API Documentation

## Overview

`luna_api.py` provides a class for Luna API requests. The Luna API is used to translate text and answer questions.

### About

This script introduces a class named `Luna` designed for Luna API requests. The Luna API facilitates text translation and question answering.

## Class: `Luna`

### Initialization

```python
def __init__(self, logger, config):
    """
    Initializes the Luna class.

    Args:
        logger (ValkyrieLogger): The logger.
        config (dict): The configuration dictionary.
    """
```

### Methods

#### `_pingUrl(self) -> str`

- Returns the ping URL.

#### `_translateUrl(self) -> str`

- Returns the translation URL.

#### `_askUrl(self) -> str`

- Returns the ask URL.

#### `async def lunaPing(self) -> dict`

- Pings the Luna API and returns information.

#### `async def lunaTranslate(self, text: str, lang: str = "en") -> dict`

- Translates text using the Luna API and returns information.
- Args:
  - `text` (str): The text to translate.
  - `lang` (str): The language to translate to. Defaults to `en`.

#### `async def lunaAsk(self, text: str) -> dict`

- Asks Luna a question using the Luna API and returns information.
- Args:
  - `text` (str): The question to ask.

## Dependencies

- [requests](https://docs.python-requests.org/en/master/): A simple HTTP library for Python.
- [base64](https://docs.python.org/3/library/base64.html): Base16, Base32, Base64, Base85 Data Encodings.

## Configuration

The Luna class relies on the Luna API configuration specified in the overall project configuration file.

## Usage

To use the Luna class for Luna API requests, create an instance of the class and call the desired methods.

Example:

```python
from Modules.luna import Luna

# Initialize Luna class
luna_instance = Luna(logger, config)

# Ping Luna API
ping_result = await luna_instance.lunaPing()
print(ping_result)

# Translate text
translation_result = await luna_instance.lunaTranslate("Hello, how are you?")
print(translation_result)

# Ask Luna a question
question_result = await luna_instance.lunaAsk("What is the meaning of life?")
print(question_result)
```
