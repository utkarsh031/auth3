from django.db import models
from members.models import *

class Event(models.Model):
    event=models.CharField(max_length=100)
    members_from_first_year=models.IntegerField()
    members_after_first_year=models.IntegerField()
    
    def __str__(self):
        return self.event
    
EVENTS = (
    ("Mashal", "Mashal"),
    ("Udgam", "Udgam"),
    ("Udyam", "Udyam"),
)


class NoticeBoard(models.Model):
    title=models.TextField(blank=False,null=False,unique=True)
    description=models.TextField(blank=False,null=False)
    date=models.DateField(auto_now=True)
    link=models.TextField(blank=False,null=False)
    event=models.CharField(max_length=100,null=False,unique=True)
    
    def _str_(self):
        return f"{self.event}-{self.title}"

class Team(models.Model):
    teamname=models.CharField(max_length=100,blank=False,null=False)
    event=models.ForeignKey(Event,on_delete=models.CASCADE)
    leader=models.ForeignKey(User,on_delete=models.CASCADE)
    member1=models.ForeignKey(User,on_delete=models.CASCADE,blank=True,null=True,related_name="member1")
    member2=models.ForeignKey(User,on_delete=models.CASCADE,blank=True,null=True,related_name="member2")
    
    def _str_(self):
        return f"{self.event}-{self.teamname}"
    
    