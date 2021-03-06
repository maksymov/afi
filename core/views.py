# -*- coding: utf-8 -*-

from __future__ import unicode_literals

# from django.shortcuts import render
import json
import re
import urllib
#import prettytable
from django.db.models import Count
from django.db.models import Q
from django.http import HttpResponse
from django.utils import translation
from django.utils.translation import ugettext as _
from core.models import *
from datetime import datetime


langs = ["ru", "en"]

def set_locale(message=None, discord_server_id=None, discord_id=None):
    if message:
        discord_server_id = message.guild.id
        discord_id = message.author.id
    player, created = Player.objects.get_or_create(discord_server_id=discord_server_id,
                                                   discord_id=discord_id)
    lang = Player.objects.get(discord_server_id=discord_server_id, discord_id=discord_id).lang
    if lang in langs:
        translation.activate(lang)
        return lang
    else:
        translation.activate("ru")
        return lang


def set_lang(discord_id, discord_server_id, lang):
    set_locale(discord_server_id=discord_server_id, discord_id=discord_id)
    player, created = Player.objects.get_or_create(discord_server_id=discord_server_id,
                                                   discord_id=discord_id)
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
    discord_server_id =message.guild.id
    ranks = Rank.objects.filter(discord_server_id=discord_server_id)
    msg = ""
    if not ranks:
        msg = _(u"В базе данных полка ещё не созданы звания. Создайте их!")
    for rank in ranks:
        msg += "`%s` - %s: %s; \n" % (rank.tag, rank.title, rank.desc)
    return msg


def squad_awards(message):
    set_locale(message)
    discord_server_id =message.guild.id
    awards = Award.objects.filter(discord_server_id=discord_server_id).order_by('order')
    msg = ""
    if not awards:
        msg = _(u"В базе данных полка ещё не созданы награды. Создайте их!")
    for award in awards:
        msg += "%s) `%s` - %s: %s; \n" % (award.order, award.tag, award.title, award.desc)
    return msg


def player_nick(message):
    """Привязка своего ника"""
    lang = set_locale(message)
    discord_server_id =message.guild.id
    user = message.author
    discord_id = user.id
    message_text = message.clean_content

    if re.search(r'\(.*?\)',message_text):
        wt_nick = re.search(r'\(.*?\)',message_text).group(0)[1:-1]
        player, created = Player.objects.get_or_create(
                discord_server_id=discord_server_id,
                discord_id=discord_id,
                )
        player.wt_nick = wt_nick
        player.save()
        msg = user.mention + '' + _(u'Аккаунт WarThunder привязан!')
    else:
        msg = _(u'Ник должен быть в круглых скобках. Вот так: `!ник (мой_игровой_ник)`') + ' \n'
        msg += '[' + _(u'Требования к никам') + ']'
        if lang == 'ru':
            msg += '(https://github.com/maksymov/afi/blob/master/README.md#2-%D1%82%D1%80%D0%B5%D0%B1%D0%BE%D0%B2%D0%B0%D0%BD%D0%B8%D1%8F-%D0%BA-%D0%BD%D0%B8%D0%BA%D0%B0%D0%BC) \n'
        else:
            msg += '(https://github.com/maksymov/afi/blob/master/README_en.md#2-requirements-to-nikcnames) \n'
    return msg


def player_rank_add(message):
    """Присвоение званий игрокам"""
    set_locale(message)
    rights = check_rights(message.author.roles)
    if rights == 'no':
        msg = ['err', _(u"Чего раскомандовался? У тебя нет роли '[AFI] Звания и награды'.")]
        return msg
    discord_server_id =message.guild.id
    message_text = message.clean_content
    rank_title = message_text[message_text.find("(") + 1:message_text.find(")")]
    for user in message.mentions:
        discord_id = user.id
        player, created = Player.objects.get_or_create(discord_server_id=discord_server_id,
                                                       discord_id=discord_id)
        try:
            rank = Rank.objects.get(discord_server_id=discord_server_id, title=rank_title)
        except:
            msg = ['err', _(u'Нет такого звания')]
            return msg
        try:
            player_rank = PlayerRank.objects.get(player=player, rank=rank)
        except:
            player_rank = PlayerRank.objects.create(player=player, rank=rank)
    msg = ['ok']
    return msg


def player_rank_remove(message):
    """Разжалование игрока в звании"""
    set_locale(message)
    rights = check_rights(message.author.roles)
    if rights == 'no':
        msg = ['err', _(u"Чего раскомандовался? У тебя нет роли '[AFI] Звания и награды'.")]
        return msg
    discord_server_id =message.guild.id
    message_text = message.clean_content
    rank_title = message_text[message_text.find("(") + 1:message_text.find(")")]
    for user in message.mentions:
        discord_id = user.id
        player, created = Player.objects.get_or_create(discord_server_id=discord_server_id,
                                                       discord_id=discord_id)
        try:
            rank = Rank.objects.get(discord_server_id=discord_server_id, title=rank_title)
        except:
            msg = ['err', _(u'Нет такого звания')]
            return msg
        try:
            player_rank = PlayerRank.objects.get(player=player, rank=rank).delete()
        except:
            pass
    msg = ['ok']
    return msg


def player_award_add(message=None,
        discord_server_id=None,
        user=None,
        author=None,
        award_title=None):
    """Присвоение наград игрокам"""
    if message:
        set_locale(message)
        rights = check_rights(message.author.roles)
        users = []
        if rights == 'no':
            msg = ['err', _(u"Чего раскомандовался? У тебя нет роли '[AFI] Звания и награды'.")]
            return msg, users
        discord_server_id = message.guild.id
        message_text = message.clean_content
        award_title = message_text[message_text.find("(") + 1:message_text.find(")")]
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
                top_award = PlayerAward.objects.filter(player=player).order_by('award__order').last()
                if top_award:
                    if award.order >= top_award.award.order:
                        nickname = award.tag + re.sub(tags, '', user.display_name)
                    else:
                        nickname = user.display_name
                else:
                    nickname = award.tag + user.display_name
                users.append({'user': user, 'nickname': nickname})
            except:
                msg = ['err', _(u'Нет такой награды')]
                return msg, users
            player_award = PlayerAward.objects.create(player=player, award=award)
        msg = ['ok',]
        return msg, users
    else:
        set_locale(discord_server_id=discord_server_id, discord_id=user.id)
        rights = check_rights(author.roles)
        if rights == 'no':
            msg = ['err', _(u"Чего раскомандовался? У тебя нет роли '[AFI] Звания и награды'.")]
            return msg
        discord_id = user.id
        tag_list = Award.objects.filter(
            discord_server_id=discord_server_id,
            ).values_list('tag', flat=True)
        tags = '[' + ''.join(tag_list) + ']'
        player, created = Player.objects.get_or_create(
            discord_server_id=discord_server_id,
            discord_id=discord_id
            )
        try:
            award = Award.objects.get(
                discord_server_id=discord_server_id,
                title=award_title
                )
            top_award = PlayerAward.objects.filter(player=player).order_by('award__order').last()
            if top_award:
                if award.order >= top_award.award.order:
                    nickname = award.tag + re.sub(tags, '', user.display_name)
                else:
                    nickname = None
            else:
                nickname = award.tag + user.display_name
        except:
            msg = ['err', _(u'Нет такой награды')]
            return msg
        player_award = PlayerAward.objects.create(player=player, award=award)
        msg_response = "<@!%s> получил награду `%s %s`" % (user.id, award.tag, award.title)
        msg = ['ok', msg_response, nickname]
        return msg


def player_award_delete(message):
    """Удаление наград игроков"""
    set_locale(message)
    rights = check_rights(message.author.roles)
    users = []
    if rights == 'no':
        msg = ['err', _(u"Чего раскомандовался? У тебя нет роли '[AFI] Звания и награды'.")]
        return msg, users
    discord_server_id =message.guild.id
    message_text = message.clean_content
    award_title = message_text[message_text.find("(") + 1:message_text.find(")")]
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
            msg = ['err', _(u'Нет такой награды')]
            return msg, users
        try:
            player_award = PlayerAward.objects.filter(player=player, award=award).order_by('-date_from')[0].delete()
        except:
            msg = ['err', _(u'У игрока нет такой награды')]
            return msg, users
    msg = ['ok',]
    return msg, users


def player_ranks(discord_server_id, discord_id):
    player, created = Player.objects.get_or_create(discord_server_id=discord_server_id,
                                                   discord_id=discord_id)
    ranks = PlayerRank.objects.filter(player=player)
    ranks_str = ""
    if ranks:
        for i in ranks:
            ranks_str += i.rank.tag + ' | '
    else:
        ranks_str = _(u"нет")
    return ranks_str


def player_awards(discord_server_id, discord_id, start_date=None, fin_date=None):
    player, created = Player.objects.get_or_create(discord_server_id=discord_server_id,
                                                   discord_id=discord_id)
    award_list = PlayerAward.objects.filter(player=player).values('award__tag')
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


def award_create(message):
    """Создание новой награды"""
    set_locale(message)
    rights = check_rights(message.author.roles)
    if rights == 'no':
        msg = ['err', _(u"Чего раскомандовался? У тебя нет роли '[AFI] Звания и награды'.")]
        return msg
    discord_server_id =message.guild.id
    message_text = message.clean_content
    tag = re.sub('[￼￼￼￼￼￼️￼￼￼️]', '', message_text[message_text.find("[") + 1:message_text.find("]")])
    title = message_text[message_text.find("(") + 1:message_text.find(")")]
    desc = message_text[message_text.find("<") + 1:message_text.find(">")]
    order = message_text[message_text.find("{") + 1:message_text.find("}")]
    if Award.objects.filter(discord_server_id=discord_server_id).filter(
            Q(tag=tag) | Q(title=title)).exists():
        msg = ['err', _(u"Такая награда уже есть. Названия и значки наград не должны повторяться")]
        return msg
    Award.objects.create(discord_server_id=discord_server_id,
                         tag=tag,
                         title=title,
                         desc=desc,
                         order=order)
    msg = ['ok']
    return msg


def award_delete(message):
    """Удаление награды"""
    set_locale(message)
    rights = check_rights(message.author.roles)
    if rights == 'no':
        msg = ['err', _(u"Чего раскомандовался? У тебя нет роли '[AFI] Звания и награды'.")]
        return msg
    discord_server_id =message.guild.id
    message_text = message.clean_content
    title = message_text[message_text.find("(") + 1:message_text.find(")")]
    try:
        award = Award.objects.get(discord_server_id=discord_server_id, title=title)
        award.delete()
        msg = ['ok']
    except:
        msg = ['err', _(u"Нет такой награды")]
    return msg


def award_edit(message):
    """Редактирование награды"""
    set_locale(message)
    rights = check_rights(message.author.roles)
    if rights == 'no':
        msg = ['err', _(u"Чего раскомандовался? У тебя нет роли '[AFI] Звания и награды'.")]
        return msg
    discord_server_id =message.guild.id
    message_text = message.clean_content
    title = message_text[message_text.find("(") + 1:message_text.find(")")]
    try:
        award = Award.objects.get(discord_server_id=discord_server_id, title=title)
        tag = re.sub('[￼￼￼￼￼￼️￼￼￼️]', '', message_text[message_text.find("[") + 1:message_text.find("]")])
        desc = message_text[message_text.find("<") + 1:message_text.find(">")]
        order = message_text[message_text.find("{") + 1:message_text.find("}")]
        award.tag = tag
        award.desc = desc
        award.order = order
        award.save()
        msg = ['ok']
    except:
        msg = ['err', _(u"Нет такой награды или команда дана неверно. Смотри описание бота.")]
    return msg


def rank_create(message):
    """Создание нового звания"""
    set_locale(message)
    rights = check_rights(message.author.roles)
    if rights == 'no':
        msg = ['err', _(u"Чего раскомандовался? У тебя нет роли '[AFI] Звания и награды'.")]
        return msg
    discord_server_id =message.guild.id
    message_text = message.clean_content
    tag = re.sub('[￼￼￼￼￼￼️￼￼￼️]', '', message_text[message_text.find("[") + 1:message_text.find("]")])
    title = message_text[message_text.find("(") + 1:message_text.find(")")]
    desc = message_text[message_text.find("<") + 1:message_text.find(">")]
    if Rank.objects.filter(discord_server_id=discord_server_id).filter(
            Q(tag=tag) | Q(title=title)).exists():
        msg = ['err', _(u"Такое звание уже есть. Названия и значки званий не должны повторяться")]
        return msg
    Rank.objects.create(discord_server_id=discord_server_id,
                        tag=tag,
                        title=title,
                        desc=desc)
    msg = ['ok']
    return msg


def rank_delete(message):
    """Удаление звания"""
    set_locale(message)
    rights = check_rights(message.author.roles)
    if rights == 'no':
        msg = ['err', _(u"Чего раскомандовался? У тебя нет роли '[AFI] Звания и награды'.")]
        return msg
    discord_server_id =message.guild.id
    message_text = message.clean_content
    title = message_text[message_text.find("(") + 1:message_text.find(")")]
    try:
        Rank.objects.get(discord_server_id=discord_server_id,
                title=title).delete()
        msg = ['ok']
    except:
        msg = ['err', _(u"Нет такого звания")]
    return msg


def rank_edit(message):
    """Изменение звания"""
    set_locale(message)
    rights = check_rights(message.author.roles)
    if rights == 'no':
        msg = ['err', _(u"Чего раскомандовался? У тебя нет роли '[AFI] Звания и награды'.")]
        return msg
    discord_server_id =message.guild.id
    message_text = message.clean_content
    title = message_text[message_text.find("(") + 1:message_text.find(")")]
    try:
        rank = Rank.objects.get(discord_server_id=discord_server_id, title=title)
        tag = re.sub('[￼￼￼￼￼￼️￼￼￼️]', '', message_text[message_text.find("[") + 1:message_text.find("]")])
        desc = message_text[message_text.find("<") + 1:message_text.find(">")]
        rank.tag = tag
        rank.desc = desc
        rank.save()
        msg = ['ok']
    except:
        msg = ['err', _(u"Нет такого звания")]
    return msg


def player_stat(message):
    lang = set_locale(message)
    msg = ""
    discord_server_id =message.guild.id
    for user in message.mentions:
        # получаю статку игрока с ThunderSkill
        discord_id = user.id
        user_url="https://thunderskill.com"
        if re.search(r'\<.*?\>',user.display_name):
            # получаю ник из треугольных скобок
            username = re.search(r'\<.*?\>',user.display_name).group(0)[1:-1]
        else:
            # получаю привязанный ник из базы данных
            player, created = Player.objects.get_or_create(discord_server_id=discord_server_id,
                    discord_id=discord_id)
            username = player.wt_nick
        if username:
            # если есть ник - делаю запрос на thunderskill
            base_url = "https://thunderskill.com/ru/stat/"
            url = "https://thunderskill.com/ru/stat/" + username + "/export/json"
            headers = {}
            headers['User-Agent'] = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0"
            req = urllib.request.Request(url, headers = headers)
            try:
                ts_response = urllib.request.urlopen(req)
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    msg += user.mention + ' | ' + _(u' не нашёл я такого в ThunderSkill.') \
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
                msg += user.mention + ' | [ThunderSkill](%s)\n' % (user_url) \
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
        ranks = player_ranks(discord_server_id, discord_id)
        msg += _(u'**Звания:** ') + ranks
        # получаю список наград игрока
        awards = player_awards(discord_server_id, discord_id)
        msg += _(u' **Награды:** ') + awards + '\n' + '\n'
    return msg


def get_top(discord_id, discord_server_id, start, end):
    set_locale(discord_server_id=discord_server_id, discord_id=discord_id)
    txt = "**" + _(u'ТОП 10 ИГРОКОВ') + "** \n"
    try:
        start_date = datetime.strptime(start, "%Y-%m-%d").date()
        end_date = datetime.strptime(end, "%Y-%m-%d").date()
        players = Player.objects.filter(discord_server_id=discord_server_id)
        top_list = PlayerAward.objects.filter(
                player__in=players,
                date_from__gte=start_date,
                date_from__lte=end_date
            ).values('player__discord_id').annotate(awards=Count('player')).order_by('-awards')
        for player in top_list[:10]:
            awards = player_awards(
                    discord_server_id,
                    player['player__discord_id'],
                    start_date,
                    end_date,
                    )
            username = "<@!%s>" % (player['player__discord_id'])
            awards_count = str(player['awards'])
            #x.add_row([username, awards_count, awards])
            txt += "%s | %s | %s \n" % (awards_count, username, awards)
        msg = ['ok', txt]
    except:
        msg = ['err', _(u'Команда должна выглядеть так: `!топ (ГГГГ-ММ-ДД) [ГГГГ-ММ-ДД]`')]
    return msg

