# -*- coding: utf-8 -*-

from __future__ import unicode_literals

# from django.shortcuts import render
import json
from django.db.models import Count
from django.db.models import Q
from django.http import HttpResponse
from core.models import Award
from core.models import Player
from core.models import PlayerAward
from core.models import PlayerRank
from core.models import Rank


def player_rank_add(request, discord_server_id, discord_id, rank_title):
    """Присвоение званий игрокам"""
    player, created = Player.objects.get_or_create(discord_server_id=discord_server_id,
                                                   discord_id=discord_id)
    try:
        rank = Rank.objects.get(discord_server_id=discord_server_id, title=rank_title)
    except:
        data = json.dumps({'status': 'err', 'text': u'Нет такого звания'})
        return HttpResponse(data)
    try:
        player_rank = PlayerRank.objects.get(player=player, rank=rank)
        data = json.dumps({'status': 'err', 'text': u'Звание уже было присвоено ранее'})
        return HttpResponse(data)
    except:
        player_rank = PlayerRank.objects.create(player=player, rank=rank)
    data = json.dumps({'status': 'ok', 'text': u"Звание присвоено!"})
    return HttpResponse(data)


def player_rank_delete(request, discord_server_id, discord_id, rank_title):
    """Разжалование игрока в звании"""
    player, created = Player.objects.get_or_create(discord_server_id=discord_server_id,
                                                   discord_id=discord_id)
    try:
        rank = Rank.objects.get(discord_server_id=discord_server_id, title=rank_title)
    except:
        data = json.dumps({'status': 'err', 'text': u'Нет такого звания'})
        return HttpResponse(data)
    try:
        player_rank = PlayerRank.objects.get(player=player, rank=rank).delete()
    except:
        data = json.dumps({'status': 'err', 'text': u'Звание ещё не присвоено игроку'})
        return HttpResponse(data)
    data = json.dumps({'status': 'ok', 'text': u"Игрок разжалован в звании!"})
    return HttpResponse(data)


def player_award_add(request, discord_server_id, discord_id, award_title):
    """Присвоение наград игрокам"""
    player, created = Player.objects.get_or_create(discord_server_id=discord_server_id,
                                                   discord_id=discord_id)
    try:
        award = Award.objects.get(discord_server_id=discord_server_id, title=award_title)
    except:
        data = json.dumps({'status': 'err', 'text': u'Нет такой награды', 'tag': ""})
        return HttpResponse(data)
    player_award = PlayerAward.objects.create(player=player, award=award)
    data = json.dumps({'status': 'ok', 'text': u"Награда вручена!", 'tag': award.tag})
    return HttpResponse(data)


def player_award_delete(request, discord_server_id, discord_id, award_title):
    """Удаление наград игроков"""
    player, created = Player.objects.get_or_create(discord_server_id=discord_server_id,
                                                   discord_id=discord_id)
    try:
        award = Award.objects.get(discord_server_id=discord_server_id, title=award_title)
    except:
        data = json.dumps({'status': 'err', 'text': u'Нет такой награды'})
        return HttpResponse(data)
    try:
        player_award = PlayerAward.objects.filter(player=player, award=award).order_by('-date_from')[0].delete()
        data = json.dumps({'status': 'ok', 'text': u"Награда игрока удалена!", 'tag': award.tag})
    except:
        data = json.dumps({'status': 'err', 'text': u'У игрока нет такой награды', 'tag': ''})
    return HttpResponse(data)


def player_ranks(request, discord_server_id, discord_id):
    player, created = Player.objects.get_or_create(discord_server_id=discord_server_id,
                                                   discord_id=discord_id)
    ranks = PlayerRank.objects.filter(player=player)
    ranks_str = ""
    for i in ranks:
        ranks_str += '`' + i.rank.tag + '` | '
    data = json.dumps({'status': 'ok', 'text': ranks_str})
    return HttpResponse(data)


def player_awards(request, discord_server_id, discord_id):
    player, created = Player.objects.get_or_create(discord_server_id=discord_server_id,
                                                   discord_id=discord_id)
    awards = PlayerAward.objects.filter(player=player).values('award__tag').annotate(Count('id'))
    awards_str = ""
    for i in awards:
        awards_str += '`' + i['award__tag'] + '`' + str(i['id__count']) + ' | '
    data = json.dumps({'status': 'ok', 'text': awards_str})
    return HttpResponse(data)


def award_create(request):
    """Создание новой награды"""
    if Award.objects.filter(discord_server_id=request.GET['discord_server_id']).filter(
            Q(tag=request.GET['tag']) | Q(title=request.GET['title'])).exists():
        data = json.dumps({'status': 'err', 'text': u"Такая награда уже есть. Названия и значки наград не должны повторяться"})
        return HttpResponse(data)
    Award.objects.create(discord_server_id=request.GET['discord_server_id'],
                         tag=request.GET['tag'],
                         title=request.GET['title'],
                         desc=request.GET['desc'],
                         duration=request.GET['duration'])
    data = json.dumps({'status': 'ok', 'text': u"Новая награда добавлена в базу данных полка"})
    return HttpResponse(data)


def award_delete(request):
    """Удаление награды"""
    try:
        award = Award.objects.get(discord_server_id=request.GET['discord_server_id'],
                title=request.GET['title'])
        data = json.dumps({'status': 'ok', 'text': u"Награда удалена из базы данных полка", 'tag': award.tag})
        award.delete()
    except:
        data = json.dumps({'status': 'err', 'text': u"Нет такой награды"})
    return HttpResponse(data)


def rank_create(request):
    """Создание нового звания"""
    if Rank.objects.filter(discord_server_id=request.GET['discord_server_id']).filter(
            Q(tag=request.GET['tag']) | Q(title=request.GET['title'])).exists():
        data = json.dumps({'status': 'err', 'text': u"Такое звание уже есть. Названия и значки званий не должны повторяться"})
        return HttpResponse(data)
    Rank.objects.create(discord_server_id=request.GET['discord_server_id'],
                        tag=request.GET['tag'],
                        title=request.GET['title'],
                        desc=request.GET['desc'])
    data = json.dumps({'status': 'ok', 'text': u"Новое звание добавлено в базу данных полка"})
    return HttpResponse(data)


def rank_delete(request):
    """Удаление звания"""
    try:
        Rank.objects.get(discord_server_id=request.GET['discord_server_id'],
                          title=request.GET['title']).delete()
        data = json.dumps({'status': 'ok', 'text': u"Звание удалено из базы данных полка"})
    except:
        data = json.dumps({'status': 'err', 'text': u"Нет такого звания"})
    return HttpResponse(data)
