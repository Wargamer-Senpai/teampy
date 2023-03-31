# teampy - teamspeak Matrix Chat Bot

# How to Setup

## Requirments 
- Linux or Windows (works on both)
- Python 3.5 =<
- requests required:  
  ```sh
  pip install requests 
  ```

## Installation
- Download latest Release from [Release Page](https://github.com/Wargamer-Senpai/teampy/releases)
  - Place folder to your desired location
- Open `config.py`
  - Required:
    - Enter matrix username and password (get these with the [TS5 Extractor](https://github.com/Gamer08YT/TS5Extractor))

  - Optional:
    - enter giphy api (can be optained freely from [developers giphy](https://developers.giphy.com/dashboard/))

- start main.py
- (soon with systemd service for Linux)

## Features 
- Current 
  - commands: 
    - `!gif` or `!gif <string>`, without search string will send a random gif
    - `!eth` display price of ethereum
    - `!btc` display price of bitcoin
    - `!help` display help message
  - can react to bad words in messages with a gif (default disabled)
  - admin commands:   
    - `!admin help`, display admin help 

- Planned
(everything is planned to be configureable)
  - OSS:
    - adding a setup.py for easier setup on linux
    - adding a .exe for windows for easier execution
    
  - General
    - adding a default giphy api key
    - adding the current connected teamspeak server to status
    - adding a way to set the profile of the bot
    - adding administration features (start/stop/restart bot via command, with admin whitelist)
    - self health check and (optional auto notify admins)
    - for administrator adding a possibility to interact with oss or execute certain commands
    - gather stats how much interaction the bot has 
    - welcome message for new joined user in rooms
    - change name (as soons teamspeak supports name changes)
## Contact
Matrix Chat `wargamer@myteamspeak.com` 
or just open an isssue


## Disclaimer
It is Recommended to use a Second Account or create a new account for the bot,  
because using this bot **can** result in breaking your account or getting it deleted (it shouldnt but can happen).  
Dont use the bot to Spam, Troll or something else.
