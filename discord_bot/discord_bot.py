# -*- coding: utf-8 -*-

import discord
import urllib.request
import json
import bot_settings

client = discord.Client()


def check_rights(roles):
    rights = 'no'
    for role in roles:
        if role.name == u'[AFI] Звания и награды':
            rights = 'yes'
    return rights


@client.event
async def on_message(message):
    """Отслеживание команд

    Функция запускает бота, следит какие команды отправляются
    боту и возвращает ответ в канал дискорда.
    """
    discord_server_id = message.server.id
    afi = client.user
    if afi in message.mentions:
        text = u'{0.author.mention}, запоминай: \n' \
               u'`!статка` - показываю твою статку с ThunderSkill;\n' \
               u'`!статка @<pupkin>` - покажу Васькину стату;\n' \
               u'`!полк` - покажу стату полка;\n' \
               u'`!адрес:http://адрес_полка_в_thunderskill` - ' \
               u'запоминаю, откуда брать статку полка (только владелец сервера)\n' \
               u'Пока всё, но я учусь ;)'
        msg = text.format(message)
        await client.send_message(message.channel, msg)
    # ===========================
    # ПОЛУЧЕНИЕ СТАТИСТИКИ ИГРОКА
    elif message.content.startswith(u'!статка'):
        if not message.mentions:
            message.mentions.append(message.author)
        msg = ""
        for user in message.mentions:
            discord_id = user.id
            # получаю статку игрока с ThunderSkill
            try:
                username = user.display_name[user.display_name.find("<") + 1:user.display_name.find(">")]
                base_url = "http://thunderskill.com/ru/stat/"
                url = "http://thunderskill.com/ru/stat/" + username + "/export/json"
                with urllib.request.urlopen(url) as url_link:
                    data = json.loads(url_link.read().decode())
                    msg += user.mention + ' | ' + base_url + username + '\n' \
                            + '(**РБ**) ' + str("%.2f" % data['stats']['r']['kpd']) + '; ' \
                            + '(**СБ**) ' + str("%.2f" % data['stats']['s']['kpd']) + '; ' \
                            + '(**АБ**) ' + str("%.2f" % data['stats']['a']['kpd']) + '; \n'
            except:
                msg += user.mention + ' | ' + u' не нашёл я такого в ThunderSkill.' \
                        u' Псевдоним на сервере должен повторять ник в игре ' \
                        u'и быть заключён в треугольные скобки. Например: \n `<pupkin>`, ' \
                        u'`<pupkin> (Василий)`, `[AFI]<pupkin>(Василий)` и т.д.\n \n'
            # получаю список званий игрока
            url = bot_settings.DJANGO_URL + "/player_ranks/" + discord_server_id \
                    + "/" + discord_id
            with urllib.request.urlopen(url) as url:
                data = json.loads(url.read().decode())
                if data['status'] == 'ok':
                    msg += u'**Звания:** ' + data['text']
            # получаю список наград игрока
            url = bot_settings.DJANGO_URL + "/player_awards/" + discord_server_id \
                    + "/" + discord_id
            with urllib.request.urlopen(url) as url:
                data = json.loads(url.read().decode())
                if data['status'] == 'ok':
                    msg += u' **Награды:** ' + data['text'] + '\n' + '\n'
        await client.send_message(message.channel, msg)
    # ========================
    # ПРИСВОЕНИЕ ЗВАНИЯ ИГРОКУ
    elif message.content.startswith(u'!звание+') or message.content.startswith(u'!звание-'):
        # проверяю наличие права на вручение (роль '[AFI] Звания и награды')
        rights = check_rights(message.author.roles)
        if rights == 'no':
            msg = u"Чего раскомандовался? У тебя нет роли '[AFI] Звания и награды'."
            await client.send_message(message.channel, msg)
        else:
            msg = ""
            for user in message.mentions:
                discord_id = user.id
                message_text = message.clean_content
                rank = message_text[message_text.find("(") + 1:message_text.find(")")]
                if message.content.startswith(u'!звание+'):
                    base_url = bot_settings.DJANGO_URL + "/player_rank_add/"
                else:
                    base_url = bot_settings.DJANGO_URL + "/player_rank_delete/"
                url = base_url + discord_server_id + "/" + discord_id + "/" + urllib.parse.quote_plus(rank)
                with urllib.request.urlopen(url) as url:
                    response = json.loads(url.read().decode())['text']
                msg += user.mention + ': ' + response + '\n'
            await client.send_message(message.channel, msg)
    # =======================
    # ВРУЧЕНИЕ НАГРАДЫ ИГРОКУ
    elif message.content.startswith(u'!награда+') or message.content.startswith(u'!награда-'):
        # проверяю наличие права на вручение (роль '[AFI] Звания и награды')
        rights = check_rights(message.author.roles)
        if rights == 'no':
            msg = u"Чего раскомандовался? У тебя нет роли '[AFI] Звания и награды'."
            await client.send_message(message.channel, msg)
        else:
            msg = ""
            for user in message.mentions:
                discord_id = user.id
                message_text = message.clean_content
                award = message_text[message_text.find("(") + 1:message_text.find(")")]
                if message.content.startswith(u'!награда+'):
                    base_url = bot_settings.DJANGO_URL + "/player_award_add/"
                else:
                    base_url = bot_settings.DJANGO_URL + "/player_award_delete/"
                url = base_url + discord_server_id + "/" + discord_id + "/" + urllib.parse.quote_plus(award)
                with urllib.request.urlopen(url) as url:
                    response = json.loads(url.read().decode())
                msg += user.mention + ': ' + response['text']
                tag = response['tag']
                try:
                    if message.content.startswith(u'!награда+'):
                        nickname = tag + user.display_name.replace(tag, "")
                    else:
                        nickname = user.display_name.replace(tag, "")
                    await client.change_nickname(user, nickname)
                except:
                    msg += " (изменить ник не могу, т.к. недостаточно прав)"
                msg += '\n'
            await client.send_message(message.channel, msg)
    # =========================
    # СОЗДАНИЕ ПОЛКОВОЙ НАГРАДЫ
    elif message.content.startswith(u'!добавить-награду-в-базу-данных'):
        message_text = message.clean_content
        rights = check_rights(message.author.roles)
        if rights == 'no':
            msg = u"Чего раскомандовался? У тебя нет роли '[AFI] Звания и награды'."
            await client.send_message(message.channel, msg)
        else:
            msg = ""
            tag = message_text[message_text.find("[") + 1:message_text.find("]")]
            title = message_text[message_text.find("(") + 1:message_text.find(")")]
            desc = message_text[message_text.find("<") + 1:message_text.find(">")]
            duration = message_text[message_text.find("{") + 1:message_text.find("}")]
            url = bot_settings.DJANGO_URL + "/award_create/?" \
                  + "discord_server_id=" + discord_server_id \
                  + "&tag=" + urllib.parse.quote_plus(tag) \
                  + "&title=" + urllib.parse.quote_plus(title) \
                  + "&desc=" + urllib.parse.quote_plus(desc) \
                  + "&duration=" + duration
            with urllib.request.urlopen(url) as url:
                response = json.loads(url.read().decode())
            msg = response['text']
            await client.send_message(message.channel, msg)
    # =========================
    # УДАЛЕНИЕ ПОЛКОВОЙ НАГРАДЫ
    elif message.content.startswith(u'!удалить-награду-из-базы-данных'):
        message_text = message.clean_content
        rights = check_rights(message.author.roles)
        if rights == 'no':
            msg = u"Чего раскомандовался? У тебя нет роли '[AFI] Звания и награды'."
            await client.send_message(message.channel, msg)
        else:
            title = message_text[message_text.find("(") + 1:message_text.find(")")]
            url = bot_settings.DJANGO_URL + "/award_delete/?" \
                  + "discord_server_id=" + discord_server_id \
                  + "&title=" + urllib.parse.quote_plus(title)
            with urllib.request.urlopen(url) as url:
                response = json.loads(url.read().decode())
            msg = response['text']
            await client.send_message(message.channel, msg)
    # =========================
    # СОЗДАНИЕ ПОЛКОВОГО ЗВАНИЯ
    elif message.content.startswith(u'!добавить-звание-в-базу-данных'):
        message_text = message.clean_content
        rights = check_rights(message.author.roles)
        if rights == 'no':
            msg = u"Чего раскомандовался? У тебя нет роли '[AFI] Звания и награды'."
            await client.send_message(message.channel, msg)
        else:
            msg = ""
            tag = message_text[message_text.find("[") + 1:message_text.find("]")]
            title = message_text[message_text.find("(") + 1:message_text.find(")")]
            desc = message_text[message_text.find("<") + 1:message_text.find(">")]
            url = bot_settings.DJANGO_URL + "/rank_create/?" \
                  + "discord_server_id=" + discord_server_id \
                  + "&tag=" + urllib.parse.quote_plus(tag) \
                  + "&title=" + urllib.parse.quote_plus(title) \
                  + "&desc=" + urllib.parse.quote_plus(desc)
            with urllib.request.urlopen(url) as url:
                response = json.loads(url.read().decode())
            msg = response['text']
            await client.send_message(message.channel, msg)
    # =========================
    # УДАЛЕНИЕ ПОЛКОВОГО ЗВАНИЯ
    elif message.content.startswith(u'!удалить-звание-из-базы-данных'):
        message_text = message.clean_content
        rights = check_rights(message.author.roles)
        if rights == 'no':
            msg = u"Чего раскомандовался? У тебя нет роли '[AFI] Звания и награды'."
            await client.send_message(message.channel, msg)
        else:
            title = message_text[message_text.find("(") + 1:message_text.find(")")]
            url = bot_settings.DJANGO_URL + "/rank_delete/?" \
                  + "discord_server_id=" + discord_server_id \
                  + "&title=" + urllib.parse.quote_plus(title)
            with urllib.request.urlopen(url) as url:
                response = json.loads(url.read().decode())
            msg = response['text']
            await client.send_message(message.channel, msg)
    #elif message.content.startswith(u'адрес:')\
    #        or message.content.startswith(u'!адрес:'):
    #    squad_url = message.content[7:]
    #    if message.author != message.server.owner:
    #        text = u'{0.author.mention}, ты тут не командуешь, 8==Э тебе'
    #    else:
    #        text = u'{0.author.mention}, Так точно!'
    #        discord_server_id = str(message.server.id)
    #        conn = lite.connect("afi.db")
    #        cursor = conn.cursor()
    #        sql = "SELECT * FROM squads WHERE discord_server_id=?"
    #        cursor.execute(sql, [(discord_server_id)])
    #        data=cursor.fetchall()
    #        if len(data) == 0:
    #            sql = "INSERT INTO squads VALUES (?, ?)"
    #            cursor.execute(sql, [(discord_server_id), (squad_url)])
    #        else:
    #            sql = "UPDATE squads SET squad = ? WHERE discord_server_id = ?"
    #            cursor.execute(sql, [(squad_url), (discord_server_id)])
    #        conn.commit()
    #        conn.close()
    #    msg = text.format(message)
    #    await client.send_message(message.channel, msg)
    #elif message.content.startswith(u'!полк'):
    #    discord_server_id = str(message.server.id)
    #    conn = lite.connect("afi.db")
    #    cursor = conn.cursor()
    #    sql = "SELECT * FROM squads WHERE discord_server_id=?"
    #    cursor.execute(sql, [(discord_server_id)])
    #    data = cursor.fetchall()
    #    if len(data) == 0:
    #        text = (u'Для этого сервера Discord не указан полк WarThunder. '
    #                u'Владелец сервера должен дать мне команду '
    #                u'`!адрес:http://адрес-полка-в-ThunderSkill`')
    #    else:
    #        squad_url = data[0][1]
    #        try:
    #            with urllib.request.urlopen(squad_url+'/export/json') as url:
    #                data = json.loads(url.read().decode())
    #                text = u'__**КПД:**__ ' \
    #                       + '(**РБ**) ' + str("%.2f" % data['kpd_r']) + '; ' \
    #                       + '(**СБ**) ' + str("%.2f" % data['kpd_s']) + '; ' \
    #                       + '(**АБ**) ' + str("%.2f" % data['kpd_a']) + '; ' \
    #                       + '\n' \
    #                       + u'Подробнее - ' + squad_url
    #        except:
    #            text = (u'Для этого сервера Discord не указан полк WarThunder. '
    #                    u'Владелец сервера должен дать мне команду '
    #                    u'`!адрес:http://адрес-полка-в-ThunderSkill`')
    #    conn.close()
    #    msg = text.format(message)
    #    await client.send_message(message.channel, msg)
client.run(bot_settings.BOT_TOKEN)
