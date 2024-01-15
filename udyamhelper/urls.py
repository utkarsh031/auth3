from django.contrib import admin
from django.urls import path, include
from .views import ViewallEvent,createTeamAPIView,TeamCountView,GetallnoticeView

urlpatterns = [
	path('/events/',ViewallEvent.as_view(),name="get-all-events"),
	path('/team/create/',createTeamAPIView.as_view(),name="create-team"),
    path('/team/count/',TeamCountView.as_view(),name="team-count"),
    path('/noticeboard/<str:event>',GetallnoticeView.as_view(),name="notice-board"),

]   