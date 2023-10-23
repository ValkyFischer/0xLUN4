# 0xLUN4 - The Valkyrie Bot

***0xLUN4*** is a set of Discord and Twitch bots designed to provide functionalities such as sending notifications, checking channel status, and handling user interactions in both Discord and Twitch chat.

## Table of Contents

- [About](#about)
- [Main Bot (ValkyrieBot)](#main-bot-valkyriebot)
- [Discord Bot](#discord-bot)
- [Twitch Bot](#twitch-bot)
- [Usage](#usage)
- [Community](#community)
  - [Creator](#creator)
  - [Contributions](#contributions)
  - [Acknowledgements](#acknowledgements)
- [License](#license)

## About

***0xLUN4*** is a project created by [Valky Fischer](https://valky.dev/en), designed to provide functionality for Discord and Twitch communities. The project includes:

- **Main Bot (ValkyrieBot)**: The main bot that runs Discord and Twitch bots concurrently. It handles configuration files and logs events.
- **Discord Bot**: A Discord bot that sends notifications and utilizes slash commands.
- **Twitch Bot**: A Twitch bot that checks the status of Twitch channels and responds to chat commands.

***0xLUN4*** is designed to be versatile and user-friendly, suitable for various communities and content creators.

## Main Bot (ValkyrieBot)

`ValkyrieBot.py` is the main script that runs the Discord and Twitch bots concurrently. It handles the configuration file and logger. The main features include:

- **Running Discord and Twitch Bots Concurrently**: The script runs both Discord and Twitch bots in an asyncio event loop.
- **Configuration File**: A configuration file is used to configure the bots. The configuration file includes settings for both Discord and Twitch.
- **Logger**: Logs events to a log file.

## Discord Bot

`bot_discord.py` is a Discord bot that can be used to send notifications to a Discord server. It also supports slash commands for interactions. Key features include:

- **Notifications**: Sends notifications to a Discord server when a Twitch channel goes live or offline.
- **Slash Commands**: Supports slash commands for interactions in the Discord server, including commands like `/ping`, `/discord`, `/twitch`, and `/exval`.

## Twitch Bot

`bot_twitch.py` is a Twitch bot that checks if a Twitch channel is live. It also responds to chat commands. Key features include:

- **Channel Status Checking**: Utilizes the Twitch API to check if a specific channel is live or offline.
- **Chat Commands**: Supports chat commands like `ping`, `discord`, and `exval` for user interactions.

## Usage

To use ***0xLUN4***, you'll need to configure the bots, including adding your bot tokens and other settings, and then run the `ValkyrieBot.py` script. The main bot (`ValkyrieBot`) runs the Discord and Twitch bots concurrently.

Please refer to the specific bot's documentation for more details on configuring and using them:

- [Discord Bot Documentation](./bot_discord.md)
- [Twitch Bot Documentation](./bot_twitch.md)

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
