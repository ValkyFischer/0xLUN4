# 0xLUN4 - The Valkyrie Bot

***0xLUN4*** is a set of Discord and Twitch bots designed to provide functionalities such as sending notifications, checking channel status, and handling user interactions in both Discord and Twitch chat.

## Table of Contents

- [About](#about)
- [Instances](#instances)
  - [Valkyrie Bot](#valkyrie-bot)
  - [Discord Bot](#discord-bot)
  - [Twitch Bot](#twitch-bot)
  - [Web Server](#web-server)
- [Modules](#modules)
  - [Luna API](#luna-api)
  - [Task System](#task-system)
- [Configuration](#configuration)
  - [Startup Bot](#startup-bot)
  - [Startup Options](#startup-options)
- [Example Usage](#example-usage)
- [Community](#community)
  - [Creator](#creator)
  - [Contributions](#contributions)
  - [Acknowledgements](#acknowledgements)
- [License](#license)

## About

***0xLUN4*** is a project created by [Valky Fischer](https://valky.dev/en), designed to provide functionality for Discord and Twitch communities. The project includes:

- **The Valkyrie Bot**: A Discord and Twitch bot to provide various functionalities, such as sending 
  notifications, checking channel status, and handling user interactions in both Discord and Twitch chat.
- **Web Server**: A web management system for the Valkyrie Bot, including the Twitch and Discord bot. 
  It provides web-based interfaces to monitor and control the Valkyrie Bot, Twitch bot, and Discord bot, such 
  as changing settings, creating manual tasks, and viewing logs.
- **Luna API**: An AI API that provides functions for interacting with its API, including translation and 
  question-answering.
- **Task System**: A task queue for managing asynchronous tasks within the project. It provides a queue for 
  storing tasks from Discord and Twitch, and gets processed by the Valkyrie Bot.

## Instances

### Valkyrie Bot

`bot_valkyrie.py` is the main bot script that runs the Valkyrie Bot. This bot integrates the functionalities of 
both the Discord bot and the Twitch bot. It also handles and processes tasks through a task queue, which can be 
related to either Discord or Twitch.
- [Valkyrie Bot Documentation](docs/bot_valkyrie.md)

### Discord Bot

`bot_discord.py` is a Discord bot designed for sending notifications to a Discord server. The bot utilizes the 
Discord API for sending notifications and implementing slash commands. Additionally, it employs the Twitch API 
to determine if a channel is live or offline, sending Discord notifications accordingly.
- [Discord Bot Documentation](docs/bot_discord.md)

### Twitch Bot

`bot_twitch.py` is a Twitch bot designed to check if a channel is live or not. It utilizes the Twitch API to 
determine the channel's live status and provides various chat commands for interaction.
- [Twitch Bot Documentation](docs/bot_twitch.md)

### Web Server

`bot_web.py` is a Python script that implements a web management system for the Valkyrie Bot, including the 
Twitch and Discord bot, within the **0xLUN4** project.
- [Web Server Documentation](docs/bot_web.md)

## Modules

### Luna API

`luna.py` is a Python script that implements a wrapper for the Luna API. L.U.N.A. is an AI which provides 
functions for interacting with its API, including translation and question-answering.
- [Luna API Documentation](docs/modules/luna.md)

### Task System

`tasks.py` is a Python script that implements a task queue for managing asynchronous tasks within the **0xLUN4** 
project. It provides a queue for storing tasks from Discord and Twitch, and gets processed by the Valkyrie Bot.
- [Task System Documentation](docs/modules/tasks.md)

## Configuration

To use ***0xLUN4***, you'll need to configure the bots, including adding your bot tokens and other settings, 
and then run the `ValkyrieBot.py` script. This script will initialize the bots and start the web server.
- [Configuration Documentation](docs/configuration.md)

### Startup Bot

To execute `ValkyrieBot`, use the following command:

```bash
python ValkyrieBot.py --config_file settings.json --debug False --env prod
```

### Startup Options

- `config_path` (str): The path to the configuration file.
- `debug` (bool): True if debug mode is enabled, False if debug mode is disabled.
- `env` (str): The environment. Can be either 'dev' or 'prod'. Default is 'prod'.

## Example Usage

To use `ValkyrieBot`, interact with it in your Discord server or Twitch chat using the following example commands:

1. **Check the bot's latency:**  
   - Discord: /ping
   - Twitch: !ping
   This command shows the bot's latency in milliseconds.

2. **Ask the AI any question:**  
   - Discord: /ask
   - Twitch: !ask
   This command allows you to ask the AI any question. The AI will respond with a most precise answer.

3. **The AI translates a message:**  
   - Discord: /translate
   - Twitch: !translate
    This command allows you to translate any language into english. The AI will respond with the translated message.

## Community

### Creator

This project was created by and is maintained by [Valky Fischer](https://valky.dev/en). You can reach out to the creator on the following platforms:

- [@v_lky](https://discord.gg/vky) on Discord
- [@v_lky](https://twitch.tv/v_lky) on Twitch
- [@ValkyDev](https://twitter.com/ValkyDev) on Twitter

### Contributions

Contributions to ***0xLUN4*** are welcome and appreciated. By contributing to this project, you help make it better and more useful for everyone. Here are a few guidelines to follow: [Contribution Guidelines](CONTRIBUTING.md)

### Acknowledgements

The creator would like to acknowledge the following contributors for their support and contributions to this project:

- *None*

## License

This project is licensed under the CC0-1.0 License. See the [LICENSE](LICENSE) file for details.
