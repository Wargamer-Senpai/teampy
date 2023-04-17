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
    - `!admin version`, display version of bot, and checks for new version
    - `!admin health`, checks health of bot, if there is a problem it hopefully will display it
    - `!admin stop`, stops the bot
    - `!admin restart`, restarts the bot
    - `!admin leave-room`, tells the bot to leave the current room (even privat chats)
    - `!admin stats`, display gathered stats
    - `!admin reload`, reload current config
    - `!admin autojoin`, toggle auto join for rooms and direct chats on invite to on or off
    

## Roadmap
(everything is planned to be configureable)

OS Features<br>
|Features|Status|Finished|<br>
|---|---|---|<br>
|adding a setup.py for easier setup on linux|planned|⬜️|<br>
|adding a .exe for windows for easier execution|planned|⬜️|<br>
<br>

General Features<br>
|Features|Status|Finished|<br>
|---|---|---|<br>
|adding a default giphy api key|done|✅|<br>
|adding administration features <br>(start/stop/restart bot via command, with admin whitelist)|done|✅|<br>
|gather stats how much interaction the bot has|WIP/partly finished|✅|<br>
|adding the current connected teamspeak server to status|planned|⬜️|<br>
|welcome message for new joined user in rooms|planned|⬜️|<br>
|self health check and (optional auto notify admins)|planned|⬜️|<br>
|adding a possibility for administrator to interact with oss or execute certain commands|planned|⬜️|<br>
|change name over command<br> (as soons teamspeak supports name changes)|currently not Possible|⬜️|<br>

<!--|⬜️|✅|-->

<br>

## Contact
Matrix Chat `wargamer@myteamspeak.com` 
or just open an isssue


## Disclaimer
It is Recommended to use a Second Account or create a new account for the bot,  
because using this bot **can** result in breaking your account or getting it deleted (it shouldnt but can happen).  
Dont use the bot to Spam, Troll or something else.
