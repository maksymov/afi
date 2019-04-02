# -*- coding: utf-8 -*-

from __future__ import unicode_literals

# from django.shortcuts import render
import json
import re
import urllib.request
from django.db.models import Count
from django.db.models import Q
from django.http import HttpResponse
from django.utils import translation
from django.utils.translation import ugettext as _
from core.models import *
from datetime import datetime


langs = ["ru", "en"]

def set_locale(message):
    discord_server_id = message.server.id
    discord_id = message.author.id
    player, created = Player.objects.get_or_create(discord_server_id=discord_server_id,
                                                   discord_id=discord_id)
    lang = Player.objects.get(discord_server_id=discord_server_id, discord_id=discord_id).lang
    if lang in langs:
        translation.activate(lang)
    else:
        translation.activate("ru")
    return


def set_lang(message):
    set_locale(message)
    discord_server_id = message.server.id
    discord_id = message.author.id
    player, created = Player.objects.get_or_create(discord_server_id=discord_server_id,
                                                   discord_id=discord_id)
    message_text = message.clean_content
    lang = message_text[message_text.find("(") + 1:message_text.find(")")]
    if lang in langs:
        player.lang = lang
        player.save()
        translation.activate(lang)
        msg = _(u"Да хоть по-китайски")
    else:
        msg = _(u"Я знаю только русский и английский")
    return msg


def check_rights(roles):
    rights = 'no'
    for role in roles:
        if role.name == u'[AFI] Звания и награды':
            rights = 'yes'
    return rights


def squad_ranks(message):
    set_locale(message)
    discord_server_id = message.server.id
    ranks = Rank.objects.filter(discord_server_id=discord_server_id)
    msg = ""
    if not ranks:
        msg = _(u"В базе данных полка ещё не созданы звания. Создайте их!")
    for rank in ranks:
        msg += "`%s` - %s: %s; \n" % (rank.tag, rank.title, rank.desc)
    return msg


def squad_awards(message):
    set_locale(message)
    discord_server_id = message.server.id
    awards = Award.objects.filter(discord_server_id=discord_server_id)
    msg = ""
    if not awards:
        msg = _(u"В базе данных полка ещё не созданы награды. Создайте их!")
    for award in awards:
        msg += "`%s` - %s: %s; \n" % (award.tag, award.title, award.desc)
    return msg


def player_nick(message):
    """Привязка своего ника"""
    set_locale(message)
    discord_server_id = message.server.id
    user = message.author
    discord_id = user.id
    message_text = message.clean_content
    wt_nick = message_text[message_text.find("(") + 1:message_text.find(")")]
    player, created = Player.objects.get_or_create(
            discord_server_id=discord_server_id,
            discord_id=discord_id,
            )
    player.wt_nick = wt_nick
    player.save()
    msg = user.mention + '' + _(u'Аккаунт WarThunder привязан!')
    return msg


def player_rank_add(message):
    """Присвоение званий игрокам"""
    set_locale(message)
    rights = check_rights(message.author.roles)
    if rights == 'no':
        msg = _(u"Чего раскомандовался? У тебя нет роли '[AFI] Звания и награды'.")
        return msg
    discord_server_id = message.server.id
    message_text = message.clean_content
    rank_title = message_text[message_text.find("(") + 1:message_text.find(")")]
    msg = ""
    for user in message.mentions:
        discord_id = user.id
        player, created = Player.objects.get_or_create(discord_server_id=discord_server_id,
                                                       discord_id=discord_id)
        try:
            rank = Rank.objects.get(discord_server_id=discord_server_id, title=rank_title)
        except:
            msg = _(u'Нет такого звания')
            return msg
        try:
            player_rank = PlayerRank.objects.get(player=player, rank=rank)
            msg += user.mention + _(u' Звание уже было присвоено ранее')
        except:
            player_rank = PlayerRank.objects.create(player=player, rank=rank)
            msg += user.mention + _(u"Звание присвоено!")
        msg += '\n'
    return msg


def player_rank_remove(message):
    """Разжалование игрока в звании"""
    set_locale(message)
    rights = check_rights(message.author.roles)
    if rights == 'no':
        msg = _(u"Чего раскомандовался? У тебя нет роли '[AFI] Звания и награды'.")
        return msg
    discord_server_id = message.server.id
    message_text = message.clean_content
    rank_title = message_text[message_text.find("(") + 1:message_text.find(")")]
    msg = ""
    for user in message.mentions:
        discord_id = user.id
        player, created = Player.objects.get_or_create(discord_server_id=discord_server_id,
                                                       discord_id=discord_id)
        try:
            rank = Rank.objects.get(discord_server_id=discord_server_id, title=rank_title)
        except:
            msg = _(u'Нет такого звания')
            return msg
        try:
            player_rank = PlayerRank.objects.get(player=player, rank=rank).delete()
            msg += user.mention + _(u"Игрок разжалован в звании!")
        except:
            msg += user.mention + _(u'Звание ещё не присвоено игроку')
            return msg
        msg += '\n'
    return msg


def player_award_add(message):
    """Присвоение наград игрокам"""
    set_locale(message)
    rights = check_rights(message.author.roles)
    if rights == 'no':
        msg = _(u"Чего раскомандовался? У тебя нет роли '[AFI] Звания и награды'.")
        return msg
    discord_server_id = message.server.id
    message_text = message.clean_content
    award_title = message_text[message_text.find("(") + 1:message_text.find(")")]
    msg = ""
    users = []
    tag_list = Award.objects.filter(
        discord_server_id=discord_server_id,
        ).values_list('tag', flat=True)
    tags = '[' + ''.join(tag_list) + ']'
    for user in message.mentions:
        discord_id = user.id
        player, created = Player.objects.get_or_create(
            discord_server_id=discord_server_id,
            discord_id=discord_id
            )
        try:
            award = Award.objects.get(
                discord_server_id=discord_server_id,
                title=award_title
                )
            nickname = award.tag + re.sub(tags, '', user.display_name)
            users.append({'user': user, 'nickname': nickname})
        except:
            msg = _(u'Нет такой награды')
            return msg
        player_award = PlayerAward.objects.create(player=player, award=award)
        msg += user.mention + _(u"Награда вручена!")
        msg += '\n'
    return msg, users


def player_award_delete(message):
    """Удаление наград игроков"""
    set_locale(message)
    rights = check_rights(message.author.roles)
    if rights == 'no':
        msg = _(u"Чего раскомандовался? У тебя нет роли '[AFI] Звания и награды'.")
        return msg
    discord_server_id = message.server.id
    message_text = message.clean_content
    award_title = message_text[message_text.find("(") + 1:message_text.find(")")]
    msg = ""
    users = []
    tag_list = Award.objects.filter(
        discord_server_id=discord_server_id,
        ).values_list('tag', flat=True)
    tags = '[' + ''.join(tag_list) + ']'
    for user in message.mentions:
        discord_id = user.id
        player, created = Player.objects.get_or_create(discord_server_id=discord_server_id,
                                                       discord_id=discord_id)
        try:
            award = Award.objects.get(discord_server_id=discord_server_id, title=award_title)
            nickname = re.sub(tags, '', user.display_name)
            users.append({'user': user, 'nickname': nickname})
        except:
            msg = _(u'Нет такой награды')
            return msg
        try:
            player_award = PlayerAward.objects.filter(player=player, award=award).order_by('-date_from')[0].delete()
            msg += user.mention + _(u"Награда игрока удалена!")
        except:
            msg += user.mention + _(u'У игрока нет такой награды')
        msg += '\n'
    return msg, users


def player_ranks(discord_server_id, discord_id):
    player, created = Player.objects.get_or_create(discord_server_id=discord_server_id,
                                                   discord_id=discord_id)
    ranks = PlayerRank.objects.filter(player=player)
    ranks_str = ""
    for i in ranks:
        ranks_str += '`' + i.rank.tag + '` | '
    return ranks_str


def player_awards(discord_server_id, discord_id):
    player, created = Player.objects.get_or_create(discord_server_id=discord_server_id,
                                                   discord_id=discord_id)
    awards = PlayerAward.objects.filter(player=player).values('award__tag').annotate(Count('id'))
    awards_str = ""
    for i in awards:
        awards_str += '`' + i['award__tag'] + '`' + str(i['id__count']) + ' | '
    return awards_str


def award_create(message):
    """Создание новой награды"""
    set_locale(message)
    rights = check_rights(message.author.roles)
    if rights == 'no':
        msg = _(u"Чего раскомандовался? У тебя нет роли '[AFI] Звания и награды'.")
        return msg
    discord_server_id = message.server.id
    message_text = message.clean_content
    tag = message_text[message_text.find("[") + 1:message_text.find("]")]
    title = message_text[message_text.find("(") + 1:message_text.find(")")]
    desc = message_text[message_text.find("<") + 1:message_text.find(">")]
    duration = message_text[message_text.find("{") + 1:message_text.find("}")]
    if Award.objects.filter(discord_server_id=discord_server_id).filter(
            Q(tag=tag) | Q(title=title)).exists():
        msg = _(u"Такая награда уже есть. Названия и значки наград не должны повторяться")
        return msg
    Award.objects.create(discord_server_id=discord_server_id,
                         tag=tag,
                         title=title,
                         desc=desc,
                         duration=duration)
    msg = _(u"Новая награда добавлена в базу данных полка")
    return msg


def award_delete(message):
    """Удаление награды"""
    set_locale(message)
    rights = check_rights(message.author.roles)
    if rights == 'no':
        msg = _(u"Чего раскомандовался? У тебя нет роли '[AFI] Звания и награды'.")
        return msg
    discord_server_id = message.server.id
    message_text = message.clean_content
    title = message_text[message_text.find("(") + 1:message_text.find(")")]
    try:
        award = Award.objects.get(discord_server_id=discord_server_id, title=title)
        msg = _(u"Награда удалена из базы данных полка")
        award.delete()
    except:
        msg = _(u"Нет такой награды")
    return msg


def rank_create(request):
    """Создание нового звания"""
    set_locale(message)
    rights = check_rights(message.author.roles)
    if rights == 'no':
        msg = _(u"Чего раскомандовался? У тебя нет роли '[AFI] Звания и награды'.")
        return msg
    discord_server_id = message.server.id
    message_text = message.clean_content
    tag = message_text[message_text.find("[") + 1:message_text.find("]")]
    title = message_text[message_text.find("(") + 1:message_text.find(")")]
    desc = message_text[message_text.find("<") + 1:message_text.find(">")]
    if Rank.objects.filter(discord_server_id=discord_server_id).filter(
            Q(tag=tag) | Q(title=title)).exists():
        msg = _(u"Такое звание уже есть. Названия и значки званий не должны повторяться")
        return msg
    Rank.objects.create(discord_server_id=discord_server_id,
                        tag=tag,
                        title=title,
                        desc=desc)
    msg = _(u"Новое звание добавлено в базу данных полка")
    return msg


def rank_delete(request):
    """Удаление звания"""
    set_locale(message)
    rights = check_rights(message.author.roles)
    if rights == 'no':
        msg = _(u"Чего раскомандовался? У тебя нет роли '[AFI] Звания и награды'.")
        return msg
    discord_server_id = message.server.id
    message_text = message.clean_content
    title = message_text[message_text.find("(") + 1:message_text.find(")")]
    try:
        Rank.objects.get(discord_server_id=discord_server_id,
                title=title).delete()
        msg = _(u"Звание удалено из базы данных полка")
    except:
        msg = _(u"Нет такого звания")
    return msg


def player_stat(message):
    set_locale(message)
    msg = ""
    discord_server_id = message.server.id
    for user in message.mentions:
        discord_id = user.id
        # получаю статку игрока с ThunderSkill
        try:
            username = user.display_name[user.display_name.find("<") + 1:user.display_name.find(">")]
            base_url = "http://thunderskill.com/ru/stat/"
            url = "http://thunderskill.com/ru/stat/" + username + "/export/json"
            headers = {}
            headers['User-Agent'] = "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:48.0) Gecko/20100101 Firefox/48.0"
            req = urllib.request.Request(url, headers = headers)
            json_data = urllib.request.urlopen(req).read()
            data = json.loads(json_data.decode())
            msg += user.mention + ' | ' + base_url + username + '\n' \
                    + _(u'(**АБ**) ') + str("%.2f" % data['stats']['a']['kpd']) + '; ' \
                    + _(u'(**РБ**) ') + str("%.2f" % data['stats']['r']['kpd']) + '; ' \
                    + _(u'(**СБ**) ') + str("%.2f" % data['stats']['s']['kpd']) + '; \n'
        except:
            try:
                player, created = Player.objects.get_or_create(discord_server_id=discord_server_id,
                                                       discord_id=discord_id)
                username = player.wt_nick
                base_url = "http://thunderskill.com/ru/stat/"
                url = "http://thunderskill.com/ru/stat/" + username + "/export/json"
                headers = {}
                headers['User-Agent'] = "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:48.0) Gecko/20100101 Firefox/48.0"
                req = urllib.request.Request(url, headers = headers)
                json_data = urllib.request.urlopen(req).read()
                data = json.loads(json_data.decode())
                msg += user.mention + ' | ' + base_url + username + '\n' \
                        + _(u'(**АБ**) ') + str("%.2f" % data['stats']['a']['kpd']) + '; ' \
                        + _(u'(**РБ**) ') + str("%.2f" % data['stats']['r']['kpd']) + '; ' \
                        + _(u'(**СБ**) ') + str("%.2f" % data['stats']['s']['kpd']) + '; \n'
            except:
                msg += user.mention + ' | ' + _(u' не нашёл я такого в ThunderSkill.') \
                        + _(u' Псевдоним на сервере должен повторять ник в игре ') \
                        + _(u'и быть заключён в треугольные скобки. Например: \n `<pupkin>`, ') \
                        + _(u'`<pupkin> (Василий)`, `[AFI]<pupkin>(Василий)` и т.д.') + u'\n \n'
        # получаю список званий игрока
        ranks = player_ranks(discord_server_id, discord_id)
        msg += _(u'**Звания:** ') + ranks
        # получаю список наград игрока
        awards = player_awards(discord_server_id, discord_id)
        msg += _(u' **Награды:** ') + awards + '\n' + '\n'
    return msg


def get_top(message):
    set_locale(message)
    msg = ""
    discord_server_id = message.server.id
    message_text = message.clean_content
    try:
        start = message_text[message_text.find("(") + 1:message_text.find(")")]
        start_date = datetime.strptime(start, "%Y-%m-%d").date()
        end = message_text[message_text.find("[") + 1:message_text.find("]")]
        end_date = datetime.strptime(end, "%Y-%m-%d").date()
        players = Player.objects.filter(discord_server_id=discord_server_id)
        awards = PlayerAward.objects.filter(
                player__in=players,
                date_from__gte=start_date,
                date_from__lte=end_date
            ).annotate(awards=Count('player')).order_by('player')
        for player in players:
            if awards.filter(player=player).count() > 0:
                msg += '<@!' + player.discord_id + '> | ' + str(awards.filter(player=player).count()) + '\n'
    except:
        msg += _(u'Команда должна выглядеть так: `!топ (ГГГГ-ММ-ДД) [ГГГГ-ММ-ДД]`')
    return msg

