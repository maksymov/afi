# -*- coding: utf-8 -*-

import discord
import urllib.request
import json
import bot_settings

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "afi.settings")
import django
django.setup()

from core.views import *
from django.utils.translation import ugettext as _

client = discord.Client()

stat = [u"!статка", u"!stat"]
ranks = [u"!звания", u"!ranks"]
awards = [u"!награды", u"!awards"]
rank_add = [u"!звание+", u"!rank+"]
rank_remove = [u"!звание-", u"!rank-"]
award_add = [u"!награда+", u"!award+"]
award_remove = [u"!награда-", u"!award-"]
create_award_in_database = [u"!добавить-награду-в-базу-данных", u"!create-award-in-database"]
delete_award_from_database = [u"!удалить-награду-из-базы-данных", u"!delete-award-from-database"]
create_rank_in_database = [u"!добавить-звание-в-базу-данных", u"!create-rank-in-database"]
delete_rank_from_database = [u"!удалить-звание-из-базы-данных", u"!delete-rank-from-database"]

@client.event
async def on_message(message):
    """Отслеживание команд

    Функция запускает бота, следит какие команды отправляются
    боту и возвращает ответ в канал дискорда.

    Отслеживаемые команды:
        !статка
        !звание+/!звание-
        !награда+/!награда-
        !добавить-награду-в-базу-данных
        !удалить-награду-из-базы-данных
        !добавить-звание-в-базу-данных
        !удалить-звание-из-базы-данных
    """
    discord_server_id = message.server.id
    afi = client.user
    if afi in message.mentions:
        servers = client.servers
        num = len(servers)
        text = u'{0.author.mention}, ' + _(u'вся инфа про меня здесь: ')\
               + u'<https://github.com/maksymov/afi/blob/master/README.md> \n' \
               + _(u'Discord-сервер тех. поддержки:') + ' <https://discord.gg/Gqza8FD> \n' \
               + _(u'Работаю на ') + str(num) + _(u' серверах!')
        msg = text.format(message)
        await client.send_message(message.channel, msg)
    # =======================
    # Выбор языка для сервера
    elif message.content.startswith(u'!lang'):
        msg = set_lang(message)
        await client.send_message(message.channel, msg)
    # ===========================
    # ПОЛУЧЕНИЕ СТАТИСТИКИ ИГРОКА
    elif message.content.startswith(tuple(stat)):
        if not message.mentions:
            message.mentions.append(message.author)
        msg = player_stat(message)
        await client.send_message(message.channel, msg)
    # ======================
    # СПИСОК ПОЛКОВЫХ ЗВАНИЙ
    elif message.content.startswith(tuple(ranks)):
        msg = squad_ranks(message)
        await client.send_message(message.channel, msg)
    # ======================
    # СПИСОК ПОЛКОВЫХ НАГРАД
    elif message.content.startswith(tuple(awards)):
        msg = squad_awards(message)
        await client.send_message(message.channel, msg)
    # ========================
    # ПРИСВОЕНИЕ ЗВАНИЯ ИГРОКУ
    elif message.content.startswith(tuple(rank_add)):
        msg = player_rank_add(message)
        await client.send_message(message.channel, msg)
    # ============================
    # РАЗЖАЛОВАНИЕ В ЗВАНИИ ИГРОКА
    elif message.content.startswith(tuple(rank_remove)):
        msg = player_rank_remove(message)
        await client.send_message(message.channel, msg)
    # =======================
    # ВРУЧЕНИЕ НАГРАДЫ ИГРОКУ
    #elif message.content.startswith(u'!награда+') or message.content.startswith(u'!награда-'):
    #    # проверяю наличие права на вручение (роль '[AFI] Звания и награды')
    #    rights = check_rights(message.author.roles)
    #    if rights == 'no':
    #        msg = u"Чего раскомандовался? У тебя нет роли '[AFI] Звания и награды'."
    #        await client.send_message(message.channel, msg)
    #    else:
    #        msg = ""
    #        for user in message.mentions:
    #            discord_id = user.id
    #            message_text = message.clean_content
    #            award = message_text[message_text.find("(") + 1:message_text.find(")")]
    #            if message.content.startswith(u'!награда+'):
    #                base_url = bot_settings.DJANGO_URL + "/player_award_add/"
    #            else:
    #                base_url = bot_settings.DJANGO_URL + "/player_award_delete/"
    #            url = base_url + discord_server_id + "/" + discord_id + "/" + urllib.parse.quote_plus(award)
    #            with urllib.request.urlopen(url) as url:
    #                response = json.loads(url.read().decode())
    #            msg += user.mention + ': ' + response['text']
    #            tag = response['tag']
    #            try:
    #                if message.content.startswith(u'!награда+'):
    #                    nickname = tag + user.display_name.strip(tag)
    #                else:
    #                    nickname = user.display_name.strip(tag)
    #                await client.change_nickname(user, nickname)
    #            except:
    #                msg += " (изменить ник не могу, т.к. недостаточно прав)"
    #            msg += '\n'
    #        await client.send_message(message.channel, msg)
    # =========================
    # СОЗДАНИЕ ПОЛКОВОЙ НАГРАДЫ
    elif message.content.startswith(tuple(create_award_in_database)):
        msg = award_create(message)
        await client.send_message(message.channel, msg)
    #elif message.content.startswith(u'!добавить-награду-в-базу-данных'):
    #    message_text = message.clean_content
    #    rights = check_rights(message.author.roles)
    #    if rights == 'no':
    #        msg = u"Чего раскомандовался? У тебя нет роли '[AFI] Звания и награды'."
    #        await client.send_message(message.channel, msg)
    #    else:
    #        msg = ""
    #        tag = message_text[message_text.find("[") + 1:message_text.find("]")]
    #        title = message_text[message_text.find("(") + 1:message_text.find(")")]
    #        desc = message_text[message_text.find("<") + 1:message_text.find(">")]
    #        duration = message_text[message_text.find("{") + 1:message_text.find("}")]
    #        url = bot_settings.DJANGO_URL + "/award_create/?" \
    #              + "discord_server_id=" + discord_server_id \
    #              + "&tag=" + urllib.parse.quote_plus(tag) \
    #              + "&title=" + urllib.parse.quote_plus(title) \
    #              + "&desc=" + urllib.parse.quote_plus(desc) \
    #              + "&duration=" + duration
    #        with urllib.request.urlopen(url) as url:
    #            response = json.loads(url.read().decode())
    #        msg = response['text']
    #        await client.send_message(message.channel, msg)
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
