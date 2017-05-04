# AFI - Discord-бот, который любит WarThunder

Если у вас есть сервер Discord, то пригласить 
бота к себе на сервер можно по следующей
ссылке:
[Бот AFI](https://discordapp.com/oauth2/authorize?client_id=304296578989162496&scope=bot&permissions=0)

__Требования к никам:__

Ники в Discord должны полностью соответствовать игровым.
Если нужно к ним ч-то приписать (например, имя или тип
техники) - ставим после ника звёздочку и дописываем.

__Бот реагирует на команды:__

`!статка` - возвращает статистику автора запроса
или игроков, которых он упомянет в запросе.
![статистика игрока](http://storage3.static.itmages.com/i/17/0424/h_1493021233_7679361_34f3e6bc59.png)
![статистика игроков](http://storage8.static.itmages.com/i/17/0424/h_1493021463_5087926_5af5782647.png)

`!полк` - возвращает статистику полка и ссылку 
на ThunderSkill.
![статистика полка](http://storage4.static.itmages.com/i/17/0424/h_1493019704_2755426_eb79a1fae3.png)

Чтоб смотреть статистику полка, владелец сервера должен отправить команду:

`!адрес:http://адрес-полка-в-ThunderSkill`

Например, для полка ACES:

`!адрес:http://thunderskill.com/en/squad/%5BACES%5D`

После этого бот запомнит, статистику какого полка
нужно показывать на сервере Discord.

__Установка бота на свой сервер__

Бот работает через [discord.py](https://github.com/Rapptz/discord.py).

Установка **Discord.py**:

```
sudo apt install build-essential
sudo apt install python3-pip
sudo apt install python3-dev
sudo apt install python3-setuptools
sudo apt install libffi-dev
sudo apt install git
sudo python3 -m pip install --upgrade pip
sudo python3 -m pip install -U discord.py[voice]
```

После этого клонируйте репозиторий AFI, и добавте файл settings.py
```
# -*- coding: utf-8 -*-

BOT_TOKEN = 'здесь-вписать-токен-бота'
```

__Создание БД__

В базе данных будет храниться связь сервера Discord
с адресом полка на ThunderSkill.

```python
import sqlite3 as lite
conn = lite.connect("afi.db")
cursor = conn.cursor()
cursor.execute("""CREATE TABLE squads
               (discord_server_id, squad)
               """)
conn.commit()
conn.close()
```

