# -*- coding: utf-8 -*-

from __future__ import unicode_literals

# from django.shortcuts import render
import json
import re
import urllib
#import prettytable
from django.db.models import Count, Sum
from django.db.models import Q
from django.http import HttpResponse
from django.utils import translation
from django.utils.translation import gettext as _
from core.models import *
from datetime import datetime


langs = ["ru", "en"]

def set_locale(locale):
    if locale in langs:
        translation.activate(locale)
        return locale
    else:
        translation.activate("ru")
        return locale


def check_rights(roles):
    rights = ['no', 'no']
    for role in roles:
        if role.name == u'[AFI] Звания и награды':
            rights[0] = 'yes'
        if role.name == u'[AFI] Администрирование наград':
            rights[1] = 'yes'
    return rights


#def squad_ranks(message):
#    set_locale(message)
#    discord_server_id =message.guild.id
#    ranks = Rank.objects.filter(discord_server_id=discord_server_id)
#    msg = ""
#    if not ranks:
#        msg = _(u"В базе данных полка ещё не созданы звания. Создайте их!")
#    for rank in ranks:
#        msg += "`%s` - %s: %s; \n" % (rank.tag, rank.title, rank.desc)
#    return msg


def squad_awards(locale, guild_id):
    lang = set_locale(locale)
    awards = Award.objects.filter(guild_id=guild_id).order_by('order')
    msg = ""
    if not awards:
        msg = _(u"В базе данных полка ещё не созданы награды. Создайте их!")
    for award in awards:
        msg += "%s) `%s` - %s: %s; \n" % (award.order, award.tag, award.title, award.desc)
    return msg


def get_award_choices(guild_id):
    awards = Award.objects.filter(guild_id=guild_id).order_by('order')
    return awards.values_list('title', flat=True)


def set_player_nick(locale, guild_id, user_id, nick):
    """Привязка своего ника"""
    lang = set_locale(locale)
    player, created = Player.objects.get_or_create(
        guild_id=guild_id,
        user_id=user_id)
    player.wt_nick = nick
    player.save()
    msg = "Аккаунт WarThunder `%s` привязан!" % (nick)
    return msg


def player_award_add(locale,
        guild_id=None,
        user=None,
        author=None,
        award_title=None):
    """Вручение наград игрокам"""
    lang = set_locale(locale)
    nickname = None
    rights = check_rights(author.roles)
    if rights[0] == 'no':
        msg = ['err', _(u"Чего раскомандовался? У тебя нет роли '[AFI] Звания и награды'.")]
        return msg
    user_id = user.id
    tag_list = Award.objects.filter(
        guild_id=guild_id,
        ).values_list('tag', flat=True)
    tags = '[' + ''.join(tag_list) + ']'
    player, created = Player.objects.get_or_create(
        guild_id=guild_id,
        user_id=user_id
        )
    try:
        award = Award.objects.get(
            guild_id=guild_id,
            title=award_title
            )
        top_award = PlayerAward.objects.filter(player=player).order_by('award__order').last()
        if top_award:
            if award.order >= top_award.award.order:
                nickname = award.tag + re.sub(tags, '', user.display_name)
        else:
            nickname = award.tag + user.display_name
    except:
        msg = ['err', _(u'Нет такой награды')]
        return msg
    player_award = PlayerAward.objects.create(player=player, award=award)
    msg_response = "<@!%s> получил награду %s %s" % (user.id, award.tag, award.title)
    msg = ['ok', msg_response, nickname]
    return msg


def player_award_delete(locale,
        guild_id=None,
        user=None,
        author=None,
        award_title=None):
    """Удаление наград игроков"""
    lang = set_locale(locale)
    users = []
    rights = check_rights(author.roles)
    if rights[0] == 'no':
        msg = ['err', _(u"Чего раскомандовался? У тебя нет роли '[AFI] Звания и награды'.")]
        return msg, users
    tag_list = Award.objects.filter(
        guild_id=guild_id,
        ).values_list('tag', flat=True)
    tags = '[' + ''.join(tag_list) + ']'
    user_id = user.id
    player, created = Player.objects.get_or_create(guild_id=guild_id,
                                                   user_id=user_id)
    try:
        award = Award.objects.get(guild_id=guild_id, title=award_title)
        nickname = re.sub(tags, '', user.display_name)
    except:
        msg = ['err', _(u'Нет такой награды')]
        return msg
    try:
        player_award = PlayerAward.objects.filter(player=player, award=award).order_by('-date_from')[0].delete()
    except:
        msg = ['err', _(u'У игрока нет такой награды')]
        return msg
    msg_response = "<@!%s> лишился награды %s %s" % (user_id, award.tag, award.title)
    msg = ['ok', msg_response, nickname]
    return msg


def player_awards(guild_id, user_id, start_date=None, fin_date=None, money=False):
    player, created = Player.objects.get_or_create(guild_id=guild_id,
                                                   user_id=user_id)
    award_list = PlayerAward.objects.filter(player=player).values('award__tag')
    if money:
        award_list = award_list.exclude(award__cost=0)
    if start_date:
        award_list = award_list.filter(date_from__gte=start_date)
    if fin_date:
        award_list = award_list.filter(date_from__lte=fin_date)
    awards = award_list.annotate(Count('id'))
    awards_str = ""
    if awards:
        for i in awards:
            awards_str += i['award__tag'] + str(i['id__count']) + ' | '
    else:
        awards_str = _(u"нет")
    return awards_str


def award_create(locale, guild_id, user, award_title, award_desc, award_icon, award_order):
    """Создание новой награды"""
    lang = set_locale(locale)
    rights = check_rights(user.roles)
    if rights[1] == 'no':
        msg = ['err', _(u"Чего раскомандовался? У тебя нет роли '[AFI] Администрирование наград'.")]
        return msg
    if Award.objects.filter(guild_id=guild_id).filter(
            Q(tag=award_icon) | Q(title=award_title)).exists():
        msg = ['err', _(u"Такая награда уже есть. Названия и значки наград не должны повторяться")]
        return msg
    Award.objects.create(guild_id=guild_id,
                         tag=award_icon,
                         title=award_title,
                         desc=award_desc,
                         order=award_order)
    text = '**Создана новая полковая награда:** %s. %s %s | %s' % (
        award_order,
        award_icon,
        award_title,
        award_desc
    )
    msg = ['ok', text]
    return msg


def award_delete(locale, guild_id, user, award_title):
    """Удаление награды"""
    lang = set_locale(locale)
    rights = check_rights(user.roles)
    if rights[1] == 'no':
        msg = ['err', _(u"Чего раскомандовался? У тебя нет роли '[AFI] Администрирование наград'.")]
        return msg
    try:
        award = Award.objects.get(guild_id=guild_id, title=award_title)
        award.delete()
        text = '**Удалена полковая награда:** %s %s' % (
            award.tag,
            award.title,
        )
        msg = ['ok', text]
    except:
        msg = ['err', _(u"Нет такой награды")]
    return msg


def award_edit(locale, guild_id, user, award_title, award_desc, award_icon, award_order, award_cost):
    """Редактирование награды"""
    lang = set_locale(locale)
    rights = check_rights(user.roles)
    if rights[1] == 'no':
        msg = ['err', _(u"Чего раскомандовался? У тебя нет роли '[AFI] Администрирование наград'.")]
        return msg
    try:
        award = Award.objects.get(guild_id=guild_id, title=award_title)
        award.tag = award_icon
        award.desc = award_desc
        award.order = award_order
        award.cost = award_cost
        award.save()
        text = '**Изменена полковая награда:** %s. %s %s | %s | %s' % (
            award_order,
            award_icon,
            award_title,
            award_desc,
            award_cost
        )
        msg = ['ok', text]
    except:
        msg = ['err', _(u"Нет такой награды или команда дана неверно. Смотри описание бота.")]
    return msg


#def rank_create(message):
#    """Создание нового звания"""
#    set_locale(message)
#    rights = check_rights(message.author.roles)
#    if rights[1] == 'no':
#        msg = ['err', _(u"Чего раскомандовался? У тебя нет роли '[AFI] Администрирование наград'.")]
#        return msg
#    discord_server_id =message.guild.id
#    message_text = message.clean_content
#    tag = re.sub('[￼￼￼￼￼￼️￼￼￼️]', '', message_text[message_text.find("[") + 1:message_text.find("]")])
#    title = message_text[message_text.find("(") + 1:message_text.find(")")]
#    desc = message_text[message_text.find("<") + 1:message_text.find(">")]
#    if Rank.objects.filter(discord_server_id=discord_server_id).filter(
#            Q(tag=tag) | Q(title=title)).exists():
#        msg = ['err', _(u"Такое звание уже есть. Названия и значки званий не должны повторяться")]
#        return msg
#    Rank.objects.create(discord_server_id=discord_server_id,
#                        tag=tag,
#                        title=title,
#                        desc=desc)
#    msg = ['ok']
#    return msg


#def rank_delete(message):
#    """Удаление звания"""
#    set_locale(message)
#    rights = check_rights(message.author.roles)
#    if rights[1] == 'no':
#        msg = ['err', _(u"Чего раскомандовался? У тебя нет роли '[AFI] Администрирование наград'.")]
#        return msg
#    discord_server_id =message.guild.id
#    message_text = message.clean_content
#    title = message_text[message_text.find("(") + 1:message_text.find(")")]
#    try:
#        Rank.objects.get(discord_server_id=discord_server_id,
#                title=title).delete()
#        msg = ['ok']
#    except:
#        msg = ['err', _(u"Нет такого звания")]
#    return msg


#def rank_edit(message):
#    """Изменение звания"""
#    set_locale(message)
#    rights = check_rights(message.author.roles)
#    if rights[1] == 'no':
#        msg = ['err', _(u"Чего раскомандовался? У тебя нет роли '[AFI] Администрирование наград'.")]
#        return msg
#    discord_server_id =message.guild.id
#    message_text = message.clean_content
#    title = message_text[message_text.find("(") + 1:message_text.find(")")]
#    try:
#        rank = Rank.objects.get(discord_server_id=discord_server_id, title=title)
#        tag = re.sub('[￼￼￼￼￼￼️￼￼￼️]', '', message_text[message_text.find("[") + 1:message_text.find("]")])
#        desc = message_text[message_text.find("<") + 1:message_text.find(">")]
#        rank.tag = tag
#        rank.desc = desc
#        rank.save()
#        msg = ['ok']
#    except:
#        msg = ['err', _(u"Нет такого звания")]
#    return msg


def player_stat(locale, guild_id, user, nick):
    user_id = user.id
    lang = set_locale(locale)
    msg = ""
    # получаю статку игрока с ThunderSkill
    user_url="https://thunderskill.com"
    if nick:
        username = nick
    else:
        if re.search(r'\<.*?\>',user.display_name):
            # получаю ник из треугольных скобок
            username = re.search(r'\<.*?\>',user.display_name).group(0)[1:-1]
        else:
            # получаю привязанный ник из базы данных
            player, created = Player.objects.get_or_create(guild_id=guild_id,
                    user_id=user_id)
            username = player.wt_nick
    if username:
        # если есть ник - делаю запрос на thunderskill
        mention = user.mention
        if nick:
            mention = nick
        base_url = "https://thunderskill.com/ru/stat/"
        url = "https://thunderskill.com/ru/stat/" + username + "/export/json"
        headers = {}
        headers['User-Agent'] = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0"
        req = urllib.request.Request(url, headers = headers)
        try:
            ts_response = urllib.request.urlopen(req)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                msg += mention + ' | ' + _(u' не нашёл я такого в ThunderSkill.') \
                + '[' + _(u'Требования к никам') + ']'
                if lang == 'ru':
                    msg += '(https://github.com/maksymov/afi/blob/master/README.md#2-%D1%82%D1%80%D0%B5%D0%B1%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F-%D0%BA-%D0%BD%D0%B8%D0%BA%D0%B0%D0%BC) \n'
                else:
                    msg += '(https://github.com/maksymov/afi/blob/master/README_en.md#2-requirements-to-nikcnames) \n'
            else:
                msg += 'ThunderSkill error: ' + str(e.code) + ' \n'
            ts_response = None
        except:
            msg += '[' + _(u'Требования к никам') + ']'
            if lang == 'ru':
                msg += '(https://github.com/maksymov/afi/blob/master/README.md#2-%D1%82%D1%80%D0%B5%D0%B1%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F-%D0%BA-%D0%BD%D0%B8%D0%BA%D0%B0%D0%BC) \n'
            else:
                msg += '(https://github.com/maksymov/afi/blob/master/README_en.md#2-requirements-to-nikcnames) \n'
            ts_response = None
        if ts_response:
            json_data = urllib.request.urlopen(req).read()
            data = json.loads(json_data.decode())
            user_url = base_url + username
            msg += mention + ' | [ThunderSkill](%s)\n' % (user_url) \
                    + _(u'(**АБ**) ') + str("%.2f" % data['stats']['a']['kpd']) + '; ' \
                    + _(u'(**РБ**) ') + str("%.2f" % data['stats']['r']['kpd']) + '; ' \
                    + _(u'(**СБ**) ') + str("%.2f" % data['stats']['s']['kpd']) + '; \n'
    else:
        msg += '[' + _(u'Требования к никам') + ']'
        if lang == 'ru':
            msg += '(https://github.com/maksymov/afi/blob/master/README.md#2-%D1%82%D1%80%D0%B5%D0%B1%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F-%D0%BA-%D0%BD%D0%B8%D0%BA%D0%B0%D0%BC) \n'
        else:
            msg += '(https://github.com/maksymov/afi/blob/master/README_en.md#2-requirements-to-nikcnames) \n'
    # получаю список званий игрока
    #ranks = player_ranks(guild_id, user_id)
    #msg += _(u'**Звания:** ') + ranks
    # получаю список наград игрока
    awards = player_awards(guild_id, user_id)
    if awards and not nick:
        msg += _(u' **Награды:** ') + awards + '\n' + '\n'
    return msg


def get_top(locale, guild_id, start, end):
    lang = set_locale(locale)
    seasons = [[1,2], [3,4], [5,6], [7,8], [9,10], [11,12]]
    year = datetime.now().year
    month = datetime.now().month
    if not start:
        month = [item for item in seasons if month in item][0][0]
        start = "%s-%s-01" % (year, month)
    if not end:
        end = datetime.now().strftime("%Y-%m-%d")
    txt = "**" + _(u'ТОП 10 ИГРОКОВ') + "** \n"
    txt += "С %s по %s \n" % (start, end) 
    try:
        start_date = datetime.strptime(start, "%Y-%m-%d").date()
        end_date = datetime.strptime(end, "%Y-%m-%d").date()
        players = Player.objects.filter(guild_id=guild_id)
        top_list = PlayerAward.objects.filter(
                player__in=players,
                date_from__gte=start_date,
                date_from__lte=end_date
            ).values('player__user_id').annotate(awards=Count('player')).order_by('-awards')
        for player in top_list[:10]:
            awards = player_awards(
                    guild_id,
                    player['player__user_id'],
                    start_date,
                    end_date,)
            username = "<@!%s>" % (player['player__user_id'])
            awards_count = str(player['awards'])
            #x.add_row([username, awards_count, awards])
            txt += "%s | %s | %s \n" % (awards_count, username, awards)
        msg = ['ok', txt]
    except:
        msg = ['err', _(u'Команда должна выглядеть так: `!топ (ГГГГ-ММ-ДД) [ГГГГ-ММ-ДД]`')]
    return msg


def get_money(locale, guild_id, start, end):
    lang = set_locale(locale)
    seasons = [[1,2], [3,4], [5,6], [7,8], [9,10], [11,12]]
    year = datetime.now().year
    month = datetime.now().month
    if not start:
        month = [item for item in seasons if month in item][0][0]
        start = "%s-%s-01" % (year, month)
    if not end:
        end = datetime.now().strftime("%Y-%m-%d")
    txt = "**" + _(u'ГОЛДУ ЗАРАБОТАЛИ') + "** \n"
    txt += "С %s по %s \n" % (start, end) 
    try:
        start_date = datetime.strptime(start, "%Y-%m-%d").date()
        end_date = datetime.strptime(end, "%Y-%m-%d").date()
        players = Player.objects.filter(guild_id=guild_id)
        top_list = PlayerAward.objects.filter(
                player__in=players,
                date_from__gte=start_date,
                date_from__lte=end_date,
                award__cost__gt=0
            ).values('player__user_id').annotate(awards=Sum('award__cost')).order_by('-awards')
        for player in top_list:
            awards = player_awards(
                    guild_id,
                    player['player__user_id'],
                    start_date,
                    end_date,
                    money=True)
            username = "<@!%s>" % (player['player__user_id'])
            awards_count = str(player['awards'])
            txt += "%s💰 | %s | %s \n" % (awards_count, username, awards)
        msg = ['ok', txt]
    except:
        msg = ['err', _(u'Команда должна выглядеть так: `!топ (ГГГГ-ММ-ДД) [ГГГГ-ММ-ДД]`')]
    return msg
