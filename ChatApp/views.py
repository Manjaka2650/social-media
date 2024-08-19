import json
import uuid
from django.shortcuts import redirect, render
from rest_framework.decorators import api_view,parser_classes,permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from base.models import CustomUser,Follow
from base.serializers import FollowSerializer
from .models import Room,Message,Notification
from .serializers import MessageSerializer,RoomSerializers,NotificationSerializer,UserSerializer
from rest_framework.parsers import MultiPartParser,FormParser
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from django.db.models import Q,OuterRef,Subquery

# Create your views here.
 
def CreateRoom(request):
    if request.method=='POST':
        username= request.POST['username1']
        username2= request.POST['username2']
        # room_name= request.POST['room_name']
        try:
            get_room= Room.objects.get(user1=username)
            return redirect('room',user1=username,user2=username2)
            # print(get_room)
        except Room.DoesNotExist:
            
            new_room= Room(user1=username)
            new_room.save()
            return redirect('room',user1=username,username=username)

    return render(request,'ChatApp/index.html')


@api_view(['GET'])
def messageView(request,room_name):
    get_room= Room.objects.get(room_name=room_name)    
    get_messages= Message.objects.filter(room=get_room)
    serializer=MessageSerializer(get_messages,many=True)
    return Response(serializer.data,status=200)

@api_view(['GET'])
def NotificationView(request,username):
    user= CustomUser.objects.get(username=username)
    get_notif= Notification.objects.filter(user=user).order_by('-created_at')
    n=[m for m in get_notif if m.sender != user]

    # v=[a for a in n if a.post not in n]
    serializer=NotificationSerializer(n,many=True)
    return Response(serializer.data,status=200)

@api_view(['GET'])
def getAllMessaged_user(request,username):
    try:
        user = CustomUser.objects.get(username=username)
        # getting the latest mesage timestamp for each room
        latest_message_subquery= Message.objects.filter(room=OuterRef('pk')).order_by('-timestamp').values('timestamp')[:1]
        # print('latest_message_subquery',latest_message_subquery)
        get_room= Room.objects.filter(Q(user1=user)|Q(user2=user)).annotate(last_message_time=Subquery(latest_message_subquery)).order_by('-last_message_time')
        # print(get_room)
        get_room_hehe= Room.objects.filter(Q(user1=user)|Q(user2=user)).order_by('-created_at')
        roomS=RoomSerializers(get_room_hehe,many=True,context={'request':request})
        serialize= RoomSerializers(get_room,many=True,context={'request':request})
        return  Response({'message':serialize.data,'usermessaged':roomS.data},status=200)
    except Exception as e:
        print(e)
        return Response("error",status=400)



@api_view(['POST'])
@parser_classes([MultiPartParser,FormParser])
@permission_classes([IsAuthenticated])
def createImage(request,username):
    try:
        image= request.FILES.get('image')
        room=Room.objects.get(room_name=request.data['room'])
    # username= request.data['username']
        # print(username)
        sender=CustomUser.objects.get(username=username)
    # image.name=f'{uuid.uuid1}.jpg'
        mess= Message.objects.create(image=image,sender=sender,room=room,content=request.data['message'])
        mess.save()
        # print(mess)
        serializer=MessageSerializer(mess,many=False)


        return Response(serializer.data,status=200)
    except Exception as e:
        print(e)
        return Response("error",status=400)

@api_view(['POST'])
@parser_classes([MultiPartParser,FormParser])
@permission_classes([IsAuthenticated])
def createVideo(request,username):
    try:
        video= request.FILES.get('video')
        room=Room.objects.get(room_name=request.data['room'])
    # username= request.data['username']
        # print(username)
        sender=CustomUser.objects.get(username=username)
    # image.name=f'{uuid.uuid1}.jpg'
        mess= Message.objects.create(video=video,sender=sender,room=room,content=request.data['message'])
        mess.save()
        # print(mess)
        serializer=MessageSerializer(mess,many=False)
        return Response(serializer.data,status=200)
    except Exception as e:
        print(e)
        return Response("error",status=400)

@api_view(['POST'])
@parser_classes([MultiPartParser,FormParser])
@permission_classes([IsAuthenticated])
def createAudio(request,username):
    try:
        audio= request.FILES.get('audio')
        room=Room.objects.get(room_name=request.data['room'])
    # username= request.data['username']
        # print(username)
        sender=CustomUser.objects.get(username=username)
    # image.name=f'{uuid.uuid1}.jpg'
        mess= Message.objects.create(audio=audio,sender=sender,room=room,content=request.data['message'])
        mess.save()
        # print(mess)
        serializer=MessageSerializer(mess,many=False)
        return Response(serializer.data,status=200)
    except Exception as e:
        print(e)
        return Response("error",status=400)

# create-notification 
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def deleteMessage(request,pk):
    try:
        m=Message.objects.get(id=pk)
        m.delete()
        return Response(True,status=200)
    except Exception as  e:
        print(e)
        return Response("false",status=400)

@api_view(['POST'])    
def setReadAllMessage(request,room_name,other_username):
    try:
        room= Room.objects.get(room_name=room_name)
        other_user= CustomUser.objects.get(username=other_username)
        messages= Message.objects.filter(Q(room=room)&Q(sender=other_user)&Q(is_read=False))
        for m in messages:
            m.is_read=True
            m.save()
        return Response(status=200)
    except Exception as e:
        print(e)
        return Response(status=400)
    
@api_view(['GET'])
def notifCount(request,username):

    user= CustomUser.objects.get(username=username)

    latest_message_subquery= Message.objects.filter(room=OuterRef('pk')).order_by('-timestamp').values('timestamp')[:1]
    get_room= Room.objects.filter(Q(user1=user)|Q(user2=user)).annotate(last_message_time=Subquery(latest_message_subquery)).order_by('-last_message_time')
   
    notif= Notification.objects.filter(Q(user=user)&Q(is_read=False))


    noti=[m for m in notif if m.sender != user]
   
    r= RoomSerializers(get_room,many=True,context={'request':request}) 
   
    m=[n for n in r.data if n['last_message'] and n['last_message']['sender']['username']!=user.username and n['last_message']['is_read']==False ]
    
    followers=Follow.objects.filter(user=user).values_list('follower',flat=True)
    following=Follow.objects.filter(follower=user).values_list('user',flat=True)
    not_followed_back = CustomUser.objects.filter(id__in=followers).exclude(id__in=following)
    # ser=UserSerializer(followed,many=True)
    # print(followed)

    # print('geting notif')
    
    return Response({'notif':len(noti),'message':len(m),'request':len(not_followed_back),'m':m},status=200)



@api_view(['GET'])
def allNotif(request,username):
    user= CustomUser.objects.get(username=username)
    
    notif= Notification.objects.filter(Q(user=user)&Q(is_read=False))
    
    latest_message_subquery= Message.objects.filter(room=OuterRef('pk')).order_by('-timestamp').values('timestamp')[:1]

    return Response({'last':latest_message_subquery})






@api_view(['POST'])    
def setReadNotif(request,pk):
    try:
        n= Notification.objects.get(id=pk)
        n.is_read=True
        n.save()
        return Response(status=200)
    except Exception as e:
        print(e)
        return Response(status=400)