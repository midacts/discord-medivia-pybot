# Discord Medivia Python Bot

A Discord bot written in Python for the great MMORPG we all know and love named Medivia (Based on Tibia).

This discord bot uses [Rapptz's discord.py](https://github.com/Rapptz/discord.py).

This bot is used to show what players are online in Medivia based on lists of players you care about.

## Table of Contents

- [How it Works](#how-it-works)
  - [main.py](#main.py)
  - [cogs/medivia.py](#cogs/medivia.py)
  - [config Directory](#config-directory)
  - [guild.json](#guild.json)
  - [guild_saved.json](#guild_saved.json)
- [Running the Bot](#running-the-bot)
- [Run via Docker](#run-via-docker)
- [Discord Commands](#discord-commands)

## How it Works

This discord bot has one cog which contains all the code for the medivia commands.

### main.py

This is the main entrypoint of the bot.

This file contains the following:

- Imports the token the bot will use to authenticate to discord
- Cycles through the bot's statuses (what game it shows the bot is playing in discord)
- Prints the bot is ready when the `python main.py` is run
  - 'Running`n`nBot is ready ...'.
- Loads all the cogs found in the 'cogs' folder

### cogs/medivia.py

This file has all the commands the bot provides for Medivia.

- get_lists
- new_list
- remove_list
- add_member
- get_member
- remove_member

Lastly, there is a `@tasks.loop` which is set to run every 60 seconds which is the main workhorse of the bot.
This loop runs the `medivia_online` function which pulls the online players from the Medivia website and compares that lists to the lists created for your discord via the above commands.

If there are any updates, it will update the channel associated with the list being checked.

### config Directory

When the bot is run and the Medivia discord commands are run, the results of the lists/members added/removed are stored in the `config` directory.

### {guild}.json

These files will be named after the discord server. The contents of the file look like this:

```json
{
    "Bullet Club": {
        "id": 00000000,                     # the ID of the discord server this json file is for
        "channels": {
            "Public Enemy": {
                "id": "00000000",           # the ID of the channel to send to
                "members": [
                    "Black Panther",
                    "Orall",
                    "Alf",
                    "Tookas Cryx"
            ]},
            "Watch the Throne": {
                "id": "00000000",           # the ID of the channel to send to
                "members": [
                    "Etrius",
                    "Sudden'slayer",
                    "Hasley",
            ]}
        }
    }
}
```

### {guild}_saved.json

Secondly, when the Medivia website is checked for online users, a file is updated with the latest online members for each list. The file is named after the discord server plus `_saved`. This is used so every minute the Medivia online list is checked that it won't update each discord channel each time. It will verify the last online list and only update if there are changes from this list.

## Running the Bot

Install the required python packages:

```bash
pip install beautifulsoup4 discord.py
```

Add your token as an environmental variable

```bash
export TOKEN='xxx'
```

Run the python app

```bash
python main.py
```

## Run via Docker

From the root directory of this repo, run the following commands:

To run in Alpine:

```bash
docker build -t discord-medivia-pybot -f Dockerfile-alpine .
docker run -d --name discord-medivia-pybot discord-medivia-pybot
```

To run in Ubuntu:

```bash
docker build -t discord-medivia-pybot -f Dockerfile-ubuntu .
docker run -d --name discord-medivia-pybot discord-medivia-pybot
```

Run the following command to check logs:

```bash
docker logs discord-medivia-pybot
```

## Discord Commands

Command prefix:

`med.`

Commands:

All commands are specific to the discord server the command is ran against.

- __Lists__
  - `get_lists`
    - __Description__:
      - Returns all the list for this discord server
    - __Parameters__:
      - This command does not have any parameters
    - __Example__:
      - `med.get_lists`
  - `new_list`
    - __Description__:
      - Creates a new list
    - __Parameters__:
      - __listName__:
        - The name to give the list that will be created
      - __channelId__:
        - The ID of the channel the list should be posted to
    - __Example__:
      - `med.new_lists Friends 1234567`
      - `med.new_lists "Watch the Throne" 1234567`
  - `remove_list`
    - __Description__:
      - Removes the specified list
    - __Parameters__:
      - __listName__
        - The name of the list to remove
    - __Example__:
      - `med.remove_list Friends`
      - `med.remove_list "Watch the Throne"`
- __Members__
  - `add_member`
    - __Description__:
      - Adds the specified member(s) to the specified list
    - __Parameters__:
      - __listName__
        - The name of the list to add the member(s) to
      - __*members__
        - The member(s) to add to the list
    - __Example__:
      - `med.add_member Friends "Beardtopia"`
      - `med.add_member "Inner Circle" "Beardtopia" "Silenus" "Listen Lady"`
  - `remove_member`
    - __Description__:
      - Removes the specified member(s) from the specified list
    - __Parameters__:
      - __listName__
        - The name of the list to remove the member(s) to
      - __*members__
        - The member(s) to remove from the list
    - __Example__:
      - `med.remove_member Friends "Beardtopia"`
      - `med.remove_member "Inner Circle" "Beardtopia" "Silenus" "Listen Lady"`
  - `get_members`
    - __Description__:
      - Returns all the members of the specified list
    - __Parameters__:
      - __listName__
        - The name of the list to return member(s) from
    - __Example__:
      - `med.remove_member Friends`
      - `med.remove_member "Inner Circle"`
