# -*- coding: utf-8 -*-

from __future__ import unicode_literals

# from django.shortcuts import render
import json
import urllib.request
from django.db.models import Count
from django.db.models import Q
from django.http import HttpResponse
from django.utils import translation
from django.utils.translation import ugettext as _
from core.models import *


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


def player_rank_add(message):
    """Присвоение званий игрокам"""
    set_locale(message)
    rights = check_rights(message.author.roles)
    if rights == 'no':
        msg = _(u"Чего раскомандовался? У тебя нет роли '[AFI] Звания и награды'.")
        return msg
    discord_server_id = message.server.id
    discord_id = user.id
    message_text = message.clean_content
    rank_title = message_text[message_text.find("(") + 1:message_text.find(")")]
    msg = ""
    for user in message.mentions:
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
    discord_id = user.id
    message_text = message.clean_content
    rank_title = message_text[message_text.find("(") + 1:message_text.find(")")]
    msg = ""
    for user in message.mentions:
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


def player_award_add(request, discord_server_id, discord_id, award_title):
    """Присвоение наград игрокам"""
    player, created = Player.objects.get_or_create(discord_server_id=discord_server_id,
                                                   discord_id=discord_id)
    try:
        award = Award.objects.get(discord_server_id=discord_server_id, title=award_title)
    except:
        data = json.dumps({'status': 'err', 'text': _(u'Нет такой награды'), 'tag': ""})
        return HttpResponse(data)
    player_award = PlayerAward.objects.create(player=player, award=award)
    data = json.dumps({'status': 'ok', 'text': _(u"Награда вручена!"), 'tag': award.tag})
    return HttpResponse(data)


def player_award_delete(request, discord_server_id, discord_id, award_title):
    """Удаление наград игроков"""
    player, created = Player.objects.get_or_create(discord_server_id=discord_server_id,
                                                   discord_id=discord_id)
    try:
        award = Award.objects.get(discord_server_id=discord_server_id, title=award_title)
    except:
        data = json.dumps({'status': 'err', 'text': _(u'Нет такой награды')})
        return HttpResponse(data)
    try:
        player_award = PlayerAward.objects.filter(player=player, award=award).order_by('-date_from')[0].delete()
        data = json.dumps({'status': 'ok', 'text': _(u"Награда игрока удалена!"), 'tag': award.tag})
    except:
        data = json.dumps({'status': 'err', 'text': _(u'У игрока нет такой награды'), 'tag': ''})
    return HttpResponse(data)


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
    msg = ""
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


def award_delete(request):
    """Удаление награды"""
    try:
        award = Award.objects.get(discord_server_id=request.GET['discord_server_id'],
                title=request.GET['title'])
        data = json.dumps({'status': 'ok', 'text': _(u"Награда удалена из базы данных полка"), 'tag': award.tag})
        award.delete()
    except:
        data = json.dumps({'status': 'err', 'text': _(u"Нет такой награды")})
    return HttpResponse(data)


def rank_create(request):
    """Создание нового звания"""
    if Rank.objects.filter(discord_server_id=request.GET['discord_server_id']).filter(
            Q(tag=request.GET['tag']) | Q(title=request.GET['title'])).exists():
        data = json.dumps({'status': 'err', 'text': _(u"Такое звание уже есть. Названия и значки званий не должны повторяться")})
        return HttpResponse(data)
    Rank.objects.create(discord_server_id=request.GET['discord_server_id'],
                        tag=request.GET['tag'],
                        title=request.GET['title'],
                        desc=request.GET['desc'])
    data = json.dumps({'status': 'ok', 'text': _(u"Новое звание добавлено в базу данных полка")})
    return HttpResponse(data)


def rank_delete(request):
    """Удаление звания"""
    try:
        Rank.objects.get(discord_server_id=request.GET['discord_server_id'],
                          title=request.GET['title']).delete()
        data = json.dumps({'status': 'ok', 'text': _(u"Звание удалено из базы данных полка")})
    except:
        data = json.dumps({'status': 'err', 'text': _(u"Нет такого звания")})
    return HttpResponse(data)


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
            with urllib.request.urlopen(url) as url_link:
                data = json.loads(url_link.read().decode())
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



    