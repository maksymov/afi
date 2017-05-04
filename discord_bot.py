import discord
import urllib.request
import json
import settings
import sqlite3 as lite

client = discord.Client()


# @client.event
# async def on_ready():
#     print('Logged in as')
#     print(client.user.name)
#     print(client.user.id)
#     print('------')


@client.event
async def on_message(message):
    if message.content.startswith(u'!ку'):
        counter = 0
        tmp = await client.send_message(message.channel, 'Чё надо?')
        async for log in client.logs_from(message.channel, limit=500):
            if log.author == message.author:
                counter += 1
        await client.edit_message(tmp, 'Много говоришь, '
                                       'уже {} сообщений наговорил.'.format(counter))
    elif message.content.startswith(u'адрес:')\
            or message.content.startswith(u'!адрес:'):
        squad_url = message.content[7:]
        if message.author != message.server.owner:
            text = u'{0.author.mention}, ты тут не командуешь, 8==Э тебе'
        else:
            text = u'{0.author.mention}, Так точно!'
            discord_server_id = str(message.server.id)
            conn = lite.connect("afi.db")
            cursor = conn.cursor()
            sql = "SELECT * FROM squads WHERE discord_server_id=?"
            cursor.execute(sql, [(discord_server_id)])
            data=cursor.fetchall()
            if len(data) == 0:
                sql = "INSERT INTO squads VALUES (?, ?)"
                cursor.execute(sql, [(discord_server_id), (squad_url)])
            else:
                sql = "UPDATE squads SET squad = ? WHERE discord_server_id = ?"
                cursor.execute(sql, [(squad_url), (discord_server_id)])
            conn.commit()
            conn.close()
        msg = text.format(message)
        # print(str(message.server.id))
        await client.send_message(message.channel, msg)
    elif message.content.startswith(u'!статка'):
        base_text = ''
        if not message.mentions:
            name = message.author.display_name.split('*', 1)[0]
            base_url = "http://thunderskill.com/ru/stat/"
            url = "http://thunderskill.com/ru/stat/" + name + "/export/json"
            try:
                with urllib.request.urlopen(url) as url_link:
                    data = json.loads(url_link.read().decode())
                    base_text = u'{0.author.mention} | ' + base_url + name \
                                + '\n' \
                                + '(**РБ**) ' + str("%.2f" % data['stats']['r']['kpd']) + '; ' \
                                + '(**СБ**) ' + str("%.2f" % data['stats']['s']['kpd']) + '; ' \
                                + '(**АБ**) ' + str("%.2f" % data['stats']['a']['kpd']) + '; '
            except:
                base_text = u'{0.author.mention}, не нашёл я тебя в ThunderSkill.' \
                            u' Имя в дискорде должно соответствовать шаблону.'
        else:
            for user in message.mentions:
                try:
                    name = user.display_name.split('*', 1)[0]
                    base_url = "http://thunderskill.com/ru/stat/"
                    url = "http://thunderskill.com/ru/stat/" + name + "/export/json"
                    with urllib.request.urlopen(url) as url_link:
                        data = json.loads(url_link.read().decode())
                        text = user.mention + ' | ' + base_url + name \
                            + '\n' \
                            + '(**РБ**) ' + str("%.2f" % data['stats']['r']['kpd']) + '; ' \
                            + '(**СБ**) ' + str("%.2f" % data['stats']['s']['kpd']) + '; ' \
                            + '(**АБ**) ' + str("%.2f" % data['stats']['a']['kpd']) + '; ' \
                            + '\n' \
                            + '\n'
                        base_text = base_text + text
                except:
                    text = user.mention + ' | ' + u' не нашёл я такого в ThunderSkill.' \
                                                  u' Имя в дискорде должно соответствовать шаблону.'
                    base_text = base_text + text + '\n' + '\n'
        msg = base_text.format(message)
        # print(str(message.server.id))
        await client.send_message(message.channel, msg)
    elif message.content.startswith(u'!полк'):
        discord_server_id = str(message.server.id)
        conn = lite.connect("afi.db")
        cursor = conn.cursor()
        sql = "SELECT * FROM squads WHERE discord_server_id=?"
        cursor.execute(sql, [(discord_server_id)])
        data = cursor.fetchall()
        if len(data) == 0:
            text = (u'Для этого сервера Discord не указан полк WarThunder. '
                    u'Владелец сервера должен дать мне команду '
                    u'`!адрес:http://адрес-полка-в-ThunderSkill`')
        else:
            squad_url = data[0][1]
            try:
                with urllib.request.urlopen(squad_url+'/export/json') as url:
                    data = json.loads(url.read().decode())
                    text = u'__**КПД:**__ ' \
                           + '(**РБ**) ' + str("%.2f" % data['kpd_r']) + '; ' \
                           + '(**СБ**) ' + str("%.2f" % data['kpd_s']) + '; ' \
                           + '(**АБ**) ' + str("%.2f" % data['kpd_a']) + '; ' \
                           + '\n' \
                           + u'Подробнее - ' + squad_url
            except:
                text = u'{0.author.mention}, Адрес полка в ThunderSkill указан не верно.'
        conn.close()
        msg = text.format(message)
        # print(str(message.server.id))
        await client.send_message(message.channel, msg)

client.run(settings.BOT_TOKEN)
