from .models import Event, Team, NoticeBoard
from members.models import User
from rest_framework import response,permissions,serializers
from .serializers import EventSerializer,TeamSerializer,NoticeBoardSerializer
from rest_framework.decorators import api_view
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status,request

class Inputserializer(serializers.Serializer):
    email = serializers.EmailField()
    name = serializers.CharField(required=True)
    college_name = serializers.CharField(required=True)
    year = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=True)

def checking(request):
    try:
        event = Event.objects.get(event=request.data["event"])
        leader = User.objects.get(email=request.data["leader"])
        member1 = (
            User.objects.get(email=request.data["member1"])
            if request.data["member1"]
            else None
        )
        member2 = (
            User.objects.get(email=request.data["member2"])
            if request.data["member2"]
            else None
        )

        event_teams = Team.objects.filter(event=event)

        first_yearites = 0
        second_yearites = 0

        if leader.year == "first":
            first_yearites += 1
        elif leader.year == "second":
            second_yearites += 1

        if member1 and member1.year == "first":
            first_yearites += 1
        elif member1 and member1.year == "second":
            second_yearites += 1

        if member2 and member2.year == "first":
            first_yearites += 1
        elif member2 and member2.year == "second":
            second_yearites += 1 
    except:
        if event.DoesNotExist:
            return "Event does not Exist"
    
        elif User.DoesNotExist:
            return "User does not Exist"
            
    if request.data["leader"]==request.data["member1"] or request.data["leader"]==request.data["member2"] or request.data["member2"]==request.data["member1"]:
        return "single user can't be present twice"
    elif leader!=request.user or member1!=request.user or member2!=request.user:
        return "Requsting user must be a member of team.Can't create a team which you are not part of"
    elif Team.objects.filter(teamname=request.data["teamname"],event=event).count():
        return "Team name already taken.It should be unique"  
    elif(
        event_teams.filter(leader=leader).count()
        or event_teams.filter(member1=leader).count()
        or event_teams.filter(member2=leader).count()
    ):
        return "Leader already has a team in this event"
    elif (
        event_teams.filter(leader=member1).count()
        or event_teams.filter(member1=member1).count()
        or event_teams.filter(member2=member1).count()
    ) and member1 is not None:
        return "Member 1 already has a team in this event"
    elif (
        event_teams.filter(leader=member2).count()
        or event_teams.filter(member1=member2).count()
        or event_teams.filter(member2=member2).count()
    ) and member2 is not None:
        return "Member 2 already has a team in this event"    
    elif (
        second_yearites != 0
        and first_yearites + second_yearites > event.members_after_first_year
    ):
        return (
            "Max size of a not-all-1st-yearites team is "
            + str(event.members_after_first_year)
            + " for this event"
        )
    elif second_yearites == 0 and first_yearites > event.members_from_first_year:
        return (
            "Max size of a all-1st-yearites team is "
            + str(event.members_from_first_year)
            + " for this event"
        )
    
class ViewallEvent(generics.ListAPIView): 
        queryset=Event.objects.all()
        serializer_class = EventSerializer
class createTeamAPIView(generics.ListAPIView):
        permission_classes = [IsAuthenticated]
        queryset=Team.objects.all()
        serializer_class=TeamSerializer
        
        def post(self,request):
            serializer=self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            message=checking(request)
            if message:
                return response({"error":message},status=status.HTTP_403_FORBIDDEN)
            serializer.save()
            team=Team.objects.get(
                teamname=request.data["teamname"],
                event=Event.objects.get(event=request.data["event"]),
            )
            team_info={
                "teamname":team.teamname,
                "event":team.event,
                "leader":team.leader.email,
                "member1":team.member1.email, 
                "member2":team.member2.email,
            }
class TeamCountView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = TeamSerializer
    def get(self, request, *args, **kwargs):
        res={}
        for event in Event:
            num=Team.objects.filter(event=event).count()
            res[event.event]=num
        return response(res, status=status.HTTP_200_OK)
    
class GetallnoticeView(generics.RetrieveAPIView):
    serializer_class =NoticeBoardSerializer
    queryset=NoticeBoard.objects.all()
    
    def get(self,request,event):
        if event == "all":
            eventslist = self.queryset.all()
        else:
            eventslist = self.queryset.filter(event=event)
        context = []
        for event in eventslist:
            context.append(
                {
                    "title": event.title,
                    "description": event.description,
                    "date": event.date,
                    "link": event.link,
                }
            )
        return response(context, status=status.HTTP_200_OK)
    
    
        
        
            
                  