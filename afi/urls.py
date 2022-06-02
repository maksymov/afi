# -*- coding: utf-8 -*-
from django.urls import path, re_path
from django.contrib import admin
import core.views

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
]

urlpatterns += [
    #url(r'^player_rank_add/(?P<discord_server_id>\w+)/(?P<discord_id>\w+)/(?P<rank_title>\w+)/$', core.views.player_rank_add),
    #url(r'^player_rank_remove/(?P<discord_server_id>\w+)/(?P<discord_id>\w+)/(?P<rank_title>\w+)/$', core.views.player_rank_remove),
    #url(r'^player_award_add/(?P<discord_server_id>\w+)/(?P<discord_id>\w+)/(?P<award_title>\w+)/$', core.views.player_award_add),
    #url(r'^player_award_delete/(?P<discord_server_id>\w+)/(?P<discord_id>\w+)/(?P<award_title>\w+)/$', core.views.player_award_delete),
    #url(r'^player_awards/(?P<discord_server_id>\w+)/(?P<discord_id>\w+)/$', core.views.player_awards),
    #url(r'^player_ranks/(?P<discord_server_id>\w+)/(?P<discord_id>\w+)/$', core.views.player_ranks),
    #url(r'^award_create/$', core.views.award_create),
    #url(r'^award_delete/$', core.views.award_delete),
    #url(r'^rank_create/$', core.views.rank_create),
    #url(r'^rank_delete/$', core.views.rank_delete),
]
