# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
from django.db import models


class Squad(models.Model):
    """Модель полка WarThunder

    discord_server_id - адрес сервера в дискорде
    squad_url - ссылка на полк в ThunderSkill
    """
    discord_server_id = models.CharField(max_length=255)
    squad_url = models.CharField(max_length=255)


class Rank(models.Model):
    """Звания

    Звание - это постоянный знак отличия, который присваивается
    при достижении определённого уровня. Например, при вложении в игру
    более 5000 р. игроку присваивается звание ДОНАТЕР или при достижении
    100-го уровня присваивается звание "МАРШАЛ". Придумать какие звания присваивать
    и за какие заслуги - задача командира.

    discord_server_id - идентификатор сервера в дискорде
    tag - значёк звания
    tite - название звания
    desc - описание, за что присваивается звание
    """
    discord_server_id = models.CharField(max_length=255)
    tag = models.CharField(max_length=8)
    title = models.CharField(max_length=255)
    desc = models.TextField(max_length=600, blank=True)


class Award(models.Model):
    """Награды

    Награда - это временный знак отличия, который присваивается
    за выполнение определённого задания. Например, за 5 фрагов в
    полковом сражении или за первые три-пять мест по итогам сезона
    полковых. Награды выдаются на время (неделя, сезон...).

    discord_server_id - идентификатор сервера в дискорде
    tag - значёк награды
    tite - название награды
    desc - описание, за что присваивается награда
    date_from - дата вручения награды
    duration - срок действия, указывается в днях
    """
    discord_server_id = models.CharField(max_length=255)
    tag = models.CharField(max_length=8)
    title = models.CharField(max_length=255)
    desc = models.TextField(max_length=600, blank=True)
    duration = models.CharField(max_length=600)


class Player(models.Model):
    """Игроки"""
    discord_server_id = models.CharField(max_length=255)
    discord_id = models.CharField(max_length=255)
    lang = models.CharField(max_length=255, blank=True)


class PlayerRank(models.Model):
    """Звания игроков

    При удалении игрока или звания записи также удаляются
    """
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    rank = models.ForeignKey(Rank, on_delete=models.CASCADE)


class PlayerAward(models.Model):
    """Награды игроков

    При удалении игрока или награды записи также удаляются
    """
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    award = models.ForeignKey(Award, on_delete=models.CASCADE)
    date_from = models.DateField(default=datetime.date.today)    
