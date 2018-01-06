# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from core.models import Award
from core.models import PlayerAward
from core.models import PlayerRank
from core.models import Rank
from core.models import Squad


class SquadAdmin(admin.ModelAdmin):
    pass
admin.site.register(Squad, SquadAdmin)


class RankAdmin(admin.ModelAdmin):
    pass
admin.site.register(Rank, RankAdmin)


class AwardAdmin(admin.ModelAdmin):
    pass
admin.site.register(Award, AwardAdmin)

class PlayerRankAdmin(admin.ModelAdmin):
    pass
admin.site.register(PlayerRank, PlayerRankAdmin)

class PlayerAwardAdmin(admin.ModelAdmin):
    pass
admin.site.register(PlayerAward, PlayerAwardAdmin)
