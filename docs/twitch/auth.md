# Twitch.auth Documentation

## Overview

`Twitch/auth.py` provides functionality to authorize the bot to use the Twitch API.

### About

This script introduces an `Auth` class for handling Twitch bot authorization. It includes methods to authorize the bot to use the Twitch API, get the OAuth code, and obtain the OAuth token.

## Class: `Auth`

### Initialization

```python
def __init__(self, config: dict, logger: ValkyrieLogger):
    """
    Initializes the Auth class.

    Args:
        config (dict): The configuration dictionary.
        logger (ValkyrieLogger): The logger.
    """
```

### Methods

#### `authorize(self, client_id: str, client_secret: str, redirect_uri: str, scopes: list, kind: str = "user") -> str`

- Authorizes the bot to use the Twitch API.
  - Args:
    - `client_id` (str): The client id of the bot.
    - `client_secret` (str): The client secret of the bot.
    - `redirect_uri` (str): The redirect URI of the bot.
    - `scopes` (list): The scopes of the bot.
    - `kind` (str): The kind of authorization. Can be either "user" or "bot".

#### `get_auth_code(self, client_id: str, redirect_uri: str, scopes: list) -> str`

- Gets the OAuth code for the bot. This code will be used to get the OAuth token for the bot.
  - Args:
    - `client_id` (str): The client id of the bot.
    - `redirect_uri` (str): The redirect URI of the bot.
    - `scopes` (list): The scopes of the bot.
  - Returns:
    - str: The OAuth code for the bot.

#### `get_auth_token(self, client_id: str, client_secret: str, code: str, redirect_uri: str) -> dict`

- Gets the OAuth token for the bot.
  - Args:
    - `client_id` (str): The client id of the bot.
    - `client_secret` (str): The client secret of the bot.
    - `code` (str): The OAuth code for the bot.
    - `redirect_uri` (str): The redirect URI of the bot.
  - Returns:
    - dict: The OAuth dict for the bot.

#### `refresh_token(self, client_id: str, client_secret: str, refresh_token: str) -> dict`

- Refreshes the OAuth token for the bot.
  - Args:
    - `client_id` (str): The client id of the bot.
    - `client_secret` (str): The client secret of the bot.
    - `refresh_token` (str): The refresh token for the bot.
  - Returns:
    - dict: The OAuth dict for the bot.

### Global Constants

- `CODE`: Global variable to store the OAuth code received.

## Dependencies

- [ValkyrieUtils](https://github.com/ValkyFischer/ValkyrieUtils): Utilities library for ***0xLUN4*** project.
- [json](https://docs.python.org/3/library/json.html): Standard Python JSON module.
- [http.server](https://docs.python.org/3/library/http.server.html): Standard Python HTTP server module.
- [os](https://docs.python.org/3/library/os.html): Module for interacting with the operating system.
- [socketserver](https://docs.python.org/3/library/socketserver.html): Standard Python socket server module.
- [webbrowser](https://docs.python.org/3/library/webbrowser.html): Standard Python web browser module.
- [requests](https://docs.python-requests.org/en/master/): A simple HTTP library for Python.

## Configuration

The `Auth` class relies on configuration settings provided in the overall project configuration dictionary.

## Usage

To use the `Auth` class, create an instance, and then call the `authorize` method with the required parameters.

Example:

```python
from Twitch.auth import Auth

# Create an Auth instance
twitch_auth = Auth(config, logger)

# Authorize the bot
twitch_auth.authorize(client_id, client_secret, redirect_uri, scopes, kind)
```