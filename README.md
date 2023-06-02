<div align="center">
<h1>teampy<br/><sub>a simple Matrix Chat Bot</sub></h1>

▶️ <a href="https://github.com/Wargamer-Senpai/teampy/wiki#setup">Setup</a> |
<a href="https://github.com/Wargamer-Senpai/teampy">GitHub</a> |
<a href="https://github.com/Wargamer-Senpai/teampy/wiki">Documentation</a> |
<a href="#roadmap">Roadmap</a>|
<a href="https://hub.docker.com/r/wargamersenpai/teampy">Docker Hub</a>

[![GitHub release (latest by date)](https://img.shields.io/github/v/release/wargamer-senpai/teampy?color=blueviolet&logoColor=blueviolet&logo=github&style=flat-square)]()
[![GitHub all releases](https://img.shields.io/github/downloads/wargamer-senpai/teampy/total?label=Downloads&color=blue&logo=github&logoColor=blue&style=flat-square)]()
[![GitHub Repo stars](https://img.shields.io/github/stars/wargamer-senpai/teampy?color=lightblue&logoColor=lightblue&logo=github&style=flat-square)]()
[![GitHub top language](https://img.shields.io/github/languages/top/wargamer-senpai/teampy?color=yellow&logo=python&logoColor=yellow&style=flat-square)]()
[![GitHub last commit](https://img.shields.io/github/last-commit/wargamer-senpai/teampy?color=brightgreen&logo=git&logoColor=brightgreen&style=flat-square)]()
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/wargamer-senpai/teampy/build-docker-image.yml?label=Image%20Build&logo=docker&style=flat-square)]()
</div>

<br><br><br>

![Unbenannt](https://github.com/Wargamer-Senpai/teampy/assets/77844672/8c38a5d3-7806-4129-9652-535cfcf3bc74)
***
teampy - a Python-based chat bot specially created for the Matrix Chat of teamspeak. Although its current capabilities are limited to a set of fundamental commands, it will receive more functionality from time to time.  (<a href="https://github.com/Wargamer-Senpai/teampy/wiki#commands-overview-and-examples">command overview</a>). The mindset behind the bot is centered around configurability, which is why the configuration file can sometimes feel overwhelming.

# try it yourself!
you can test the bot yourself, just add `teampy@myteamspeak.com` to your contacts

<br><br><br>
![Unbenannt_1](https://github.com/Wargamer-Senpai/teampy/assets/77844672/dd691471-e496-4792-8bb6-ae2948275d68)
***
<a href="#methode-1-docker-run">Methode 1: docker run</a><br>
<a href="#methode-2-docker-compose">Methode 2: docker-compose</a><br>
<a href="#methode-3-manuell-installation">Methode 3: Manuell Installation</a><br>

<br><br><br>
## Methode 1: docker run
create the local directorys for mounting into the container (logs is optional, but recommended)
```sh
mkdir -p /opt/teampy/configs
mkdir -p /opt/teampy/logs
``` 
run the container
```sh 
docker run -d --name teampy --restart on-failure -v /opt/teampy/configs:/opt/teampy/configs -v /opt/teampy/logs:/opt/teampy/logs wargamersenpai/teampy:latest
```
now edit the config in the mounted directory 
```
vi /opt/teampy/configs/config.py
```
enter the matrix username and password (you can get these with [TS5 Extractor](https://github.com/Gamer08YT/TS5Extractor))
```
...
matrix_username = aefaefaefaefaefa354354354354===
matrix_password = JkFpIopKKKtdf55uimne69
...
```
now you can start the container 
```sh
docker start teampy
```

<br><br><br>
## Methode 2: docker-compose
create the local directorys for mounting into the container (logs is optional, but recommended)
```sh
mkdir -p /opt/teampy/configs
mkdir -p /opt/teampy/logs
``` 
create a `docker-compose.yml` with following content
```yml
version: '3'
services:
  teampy:
    image: wargamersenpai/teampy:latest
    container_name: teampy
    restart: on-failure
    volumes:
      - /opt/teampy/configs:/opt/teampy/configs
      - /opt/teampy/logs:/opt/teampy/logs
```

now you can run docker-compose (in the same directory where the yml file is located)
```
docker-compose up -d
```
after that, edit the config in the mounted directory 
```
vi /opt/teampy/configs/config.py
```
enter the matrix username and password (you can get these with [TS5 Extractor](https://github.com/Gamer08YT/TS5Extractor))
```
...
matrix_username = aefaefaefaefaefa354354354354===
matrix_password = JkFpIopKKKtdf55uimne69
...
```
now you can start the container 
```sh
docker start teampy
```

<br><br><br>

## Methode 3: Manuell Installation
### Requirments 
- Linux or Windows (works on both)
- Python 3.5 =<
- module requests required:  
  ```sh
  pip install requests 
  ```

### Installation
- Download latest Release from [Release Page](https://github.com/Wargamer-Senpai/teampy/releases)
  - Place folder to your desired location
  - move teampy.service into /etc/systemd/system
  ```sh
  mv ./teampy.service /etc/systemd/system 
  ```
  - edit the `teampy.service` and adjust the directory where the `main.py` is located at
  ```sh
  vi /etc/systemd/system/teampy.service
  ```
  ```sh
  ...
  [Service]
  ExecStart=/usr/bin/python3 /dir/to/main.py
  ...  
  ``` 
- Open `config.py`
  - Required:
    - Enter matrix username and password (get these with the [TS5 Extractor](https://github.com/Gamer08YT/TS5Extractor))

  - Optional:
    - enter giphy api (can be optained freely from [developers giphy](https://developers.giphy.com/dashboard/))

- start main.py with systemd service 
```sh
systemctl enable --now teampy.service
```
<br><br><br>

![Unbenannt_5](https://github.com/Wargamer-Senpai/teampy/assets/77844672/2674787b-c351-4227-a9ce-e565ecce99b6)
***

- Current 
  - commands: 
    - `!gif` or `!gif <string>`, without search string will send a random gif
    - `!stats` display gathered stats
    - `!eth` display price of ethereum
    - `!btc` display price of bitcoin
    - `!help` display help message
    - `!whoami` display help message
    - `!whois <identifier>` display help message
    - `!roll` roll a dice
    - `!poll <question>` post a poll where user can vote with emojis more info [here](https://github.com/Wargamer-Senpai/teampy/wiki/Overview#poll-string)
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
 
<br><br><br>

## Roadmap
(everything is planned to be configureable)

OS Features<br>
|Features|Status|Finished|
|---|---|---|
|adding a setup.sh for easier setup on linux|planned|⬜️|
|adding systemd service |done|✅|
|adding a .exe for windows for easier execution|planned|⬜️|
|adding a container image|done|✅|
<br>

General Features<br>
|Features|Status|Finished|
|---|---|---|
|adding a default giphy api key|done|✅|
|adding administration features <br>(start/stop/restart bot via command, with admin whitelist)|done|✅|
|gather stats how much interaction the bot has|partly finished|✅|
|adding a check for new version of the teamspeak client|in Work/partly finished|⬜️|
|adding the current connected teamspeak server to status|planned|⬜️|
|welcome message for new joined user in rooms|planned|⬜️|
|self health check and (optional auto notify admins)|partly finished|⬜️|
|adding a possibility for administrator to interact with oss or execute certain commands|planned|⬜️|
|change name over command<br> (as soons teamspeak supports name changes)|currently not Possible|⬜️|

<!--|⬜️|✅|-->

<br>

## Contact
Matrix Chat `wargamer@myteamspeak.com` 
or just open an isssue

<br><br><br>

![Unbenannt_3](https://github.com/Wargamer-Senpai/teampy/assets/77844672/c56eb363-f74d-4586-a714-79cce58f77b8)
***
It is Recommended to use a Second Account or create a new account for the bot,  
because using this bot **can** result in breaking your account (it shouldnt but can happen).  

