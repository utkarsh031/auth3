from django.contrib import admin

from .models import Team,NoticeBoard,Event

admin.site.register(Team)
admin.site.register(Event)
admin.site.register(NoticeBoard)
