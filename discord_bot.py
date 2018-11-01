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

nick = [u"!ник", u"!nick"]
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
    # ======================
    # ПРИВЯЗКА ИГРОВОГО НИКА
    elif message.content.startswith(tuple(nick)):
        msg = player_nick(message)
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
    elif message.content.startswith(tuple(award_add)):
        msg, users = player_award_add(message)
        for u in users:
            try:
                await client.change_nickname(u['user'], u['nickname'])
            except:
                pass
        await client.send_message(message.channel, msg)
    # =======================
    # ОТБОР НАГРАДЫ ИГРОКА
    elif message.content.startswith(tuple(award_remove)):
        msg, users = player_award_delete(message)
        for u in users:
            try:
                await client.change_nickname(u['user'], u['nickname'])
            except:
                pass
        await client.send_message(message.channel, msg)
    # =========================
    # СОЗДАНИЕ ПОЛКОВОЙ НАГРАДЫ
    elif message.content.startswith(tuple(create_award_in_database)):
        msg = award_create(message)
        await client.send_message(message.channel, msg)
    # =========================
    # УДАЛЕНИЕ ПОЛКОВОЙ НАГРАДЫ
    elif message.content.startswith(tuple(delete_award_from_database)):
        msg = award_delete(message)
        await client.send_message(message.channel, msg)
    # =========================
    # СОЗДАНИЕ ПОЛКОВОГО ЗВАНИЯ
    elif message.content.startswith(tuple(create_rank_in_database)):
        msg = rank_create(message)
        await client.send_message(message.channel, msg)
    # =========================
    # УДАЛЕНИЕ ПОЛКОВОГО ЗВАНИЯ
    elif message.content.startswith(tuple(delete_rank_from_database)):
        msg = rank_delete(message)
        await client.send_message(message.channel, msg)
client.run(bot_settings.BOT_TOKEN)
