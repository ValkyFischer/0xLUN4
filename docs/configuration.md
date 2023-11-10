# Configuration Documentation

This document outlines the overall project configuration for the Valkyrie bot management system. The configuration is stored in a JSON file and contains settings for Twitch integration, Discord integration, task intervals, Luna (backend service) configuration, and web server settings.

## Twitch

The Twitch configuration section includes settings related to the Twitch API, bot credentials, channel details, bot command prefix, available rewards, and required scopes.

```json
"twitch": {
    "user": {
        "client_id": "your_user_client_id",
        "client_secret": "your_user_client_secret"
    },
    "bot": {
        "client_id": "your_bot_client_id",
        "client_secret": "your_bot_client_secret"
    },
    "api_uri": "https://api.twitch.tv/helix",
    "redirect_uri": "http://localhost:8000",
    "channel": "v_lky",
    "prefix": "!",
    "rewards": [
        {
            "name": "timeout for 5 minutes",
            "task": "twitch_timeout",
            "time": 300,
            "instant": true
        },
        // ... other rewards ...
    ],
    "scopes": {
        // ... Twitch API scopes ...
    }
}
```

## Discord 

The Discord configuration section includes settings for the Discord bot, such as the bot token, guild ID, and channel IDs for different purposes.

```json
"discord": {
    "bot_token": "your_discord_bot_token",
    "guild_id": "your_discord_guild_id",
    "channels": {
        "admin": "admin_channel_id",
        "commands": "commands_channel_id",
        "stream": "stream_channel_id"
    }
}
```

## Interval

The `interval` setting specifies the time interval (in seconds) for various periodic tasks.

```json
"interval": 60
```

## Luna

The Luna configuration section includes settings for the Luna backend service, such as the host, port, version, token, and interval.

```json
"luna": {
    "host": "valky.dev",
    "port": 443,
    "version": 2,
    "token": "your_luna_token",
    "interval": 3600
}
```

## Web Server

The web server configuration section includes settings for the Valkyrie bot's web management interface, such as the host, port, login credentials, and token.

```json
"web": {
    "host": "0.0.0.0",
    "port": 5001,
    "user": "your_web_user",
    "pass": "your_web_password",
    "token": "your_web_token"
}
```
