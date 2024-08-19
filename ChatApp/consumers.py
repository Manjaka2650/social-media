import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import * 
from .serializers import MessageSerializer,NotificationSerializer
from django.db.models import Q,OuterRef,Subquery

class ChatConsumer(AsyncWebsocketConsumer):
    connected_users={}
    async def connect(self):
        # get the room name from url
        self.room_name=self.scope['url_route']['kwargs']['room_name']
        self.room_group_name=f'chat_{self.room_name}'
        self.room=await self.get_room()
        self.user=self.scope['user']
        if self.room:
            await self.channel_layer.group_add(self.room_group_name,self.channel_name)
            if self.room_group_name not in self.connected_users:
                self.connected_users[self.room_group_name]=set()
            self.connected_users[self.room_group_name].add(self.user.username)
            await self.accept()
        else:
            await  self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name,self.channel_name)
        if self.room_group_name not in self.connected_users:
            self.connected_users[self.room_group_name].discard(self.user.username)
            if not self.connected_users[self.room_group_name]:
                del self.connected_users[self.room_group_name]
                
        

    async def receive(self,text_data):
        text_data_json= json.loads(text_data)
        event_type= text_data_json.get('type')
        print(text_data_json)
        if event_type=='send_message':
            # print(event_type)
            await self.handle_receiving_message(text_data_json)
        
        elif event_type=='typing':
            # print(event_type)
            await self.handle_isTyping_message(text_data_json)
        elif event_type=='delete_message':
            await self.handle_delete_message(text_data_json)

        elif event_type=='set_read_message':
            await self.handle_set_read_message(text_data_json)
            # pass
            



# if the event type is sending data
    async def handle_receiving_message(self,data):
        message= data['message']
        sender_username= data['sender']
        new_message= data['new_message']

        print(message)

        sender= await self.get_user(sender_username)
# si ce n'est pas un nouveau message mais un message deja creer
        if not new_message:
            new_message=await self.create_message(self.room,sender,message)
        event={
            'type':'send_message',
            'message':new_message,
            'sender':sender_username
            }
        await self.channel_layer.group_send(self.room_group_name,event)


# if the event type is typing message
    async def handle_isTyping_message(self,data):
        # data from the fornt-end
        isT= data.get('isTyping',False)
        sender_username= data.get('sender')
        print(isT)
        # print(sender_username)
        
        event={
            'type':'typing',
            'isTyping':isT,
            'sender':sender_username
            }
        await self.channel_layer.group_send(self.room_group_name,event)

# if the event is delete message
    async def handle_delete_message(self,data):
        messageid= data['messageid']
        event={
            'type':'delete_message',
            'messageid':messageid
        }
        await self.channel_layer.group_send(self.room_group_name,event)
        pass

# if the event is set read all messages
    async def handle_set_read_message(self,data):
        other_username=data['other_user']
        event={'type':'set_read_message','other_username':other_username}
        await self.channel_layer.group_send(self.room_group_name,event)


# fonction pour send_message
    async def send_message(self,event):        
        message= event['message']
        sender= event['sender']
        # await self.create_message(data={"message":message,"sender":sender})
        response_data={
            "sender":sender,
            "message":message
        }
        await self.send(text_data=json.dumps({"type":'message','message':response_data}))

# fonction pour typing
    async def typing(self,event):
        user=event['sender']
        isTyping= event['isTyping']
        response_data={
            'user':user,
            'isTyping':isTyping
        }
        # celui qui defini ce qu'on fait et que le frontend recevera
        await self.send(text_data=json.dumps({'type':'typing','isTyping':response_data}))

# fonction pour delete message
    async def delete_message(self,event):
        messageid= event['messageid']
        m=await self.get_delete_message(pk=messageid)
        # await m.delete()
        await self.send(text_data=json.dumps({'type':'delete_message','messageid':messageid}))

    async def set_read_message(self,event):
        other_username=event['other_username']
        await self.set_read_messages(other_username)
        await self.send(text_data=json.dumps({'type':'set_read_message','readed':True}))

    @database_sync_to_async
    def get_room(self):
        try:
            get =  Room.objects.get(room_name=self.room_name)
            return get
        except Room.DoesNotExist:
            return None
    @database_sync_to_async
    def get_user(self,username):
        try:
            get =  CustomUser.objects.get(username=username)
            return get
        except CustomUser.DoesNotExist:
            return None
        
    @database_sync_to_async
    def create_message(self,room,sender,content):
        # creer  le message puis la sauvegarde avec les trucs aproprie
        new_message= Message.objects.create(room=room,sender=sender,content=content)
        new_message.save()
        return MessageSerializer(new_message,many=False).data

    @database_sync_to_async
    def get_delete_message(self,pk):
        try:
            get =  Message.objects.get(id=pk)
            get.delete()
            return get
        except Message.DoesNotExist:
            return None
         
    @database_sync_to_async
    def set_read_messages(self,other_username):
        other_user= CustomUser.objects.get(username=other_username)
        messages= Message.objects.filter(Q(room=self.room)&Q(sender=other_user)&Q(is_read=False))
        for m in messages:
            m.is_read=True
            m.save()



class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # get the room name from url
        self.username=self.scope['url_route']['kwargs']['username']
        self.group_name=f'notification_{self.username}'

        self.user=await self.get_user(self.username)
        
        if self.user:
            await self.channel_layer.group_add(self.group_name,self.channel_name)
            await self.accept()
        else:
            await  self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name,self.channel_name)

    async def receive(self,text_data):
        text_data_json= json.loads(text_data)
        action= text_data_json['action']
        sender_username= text_data_json['sender']
        postid= text_data_json['postId']
        content=action
        
        sender= await self.get_user(username=sender_username)
        post= await self.get_post(postid=postid)
        # en reception nous creeons la notif puis l'envoye apres
        new_notification=await self.create_Notification(self.user,sender,content,post)
        event={
            'type':'send_notif',
            'notif':new_notification,
            'sender':sender_username

        }
        await self.channel_layer.group_send(self.group_name,event)


    async def send_message(self,event):        
        notif= event['notif']
        sender= event['sender']
        # await self.create_message(data={"message":message,"sender":sender})
        response_data={
            "sender":sender,
            "notif":notif
        }
        await self.send(text_data=json.dumps({'notification':response_data}))

    @database_sync_to_async
    def get_user(self,username):
        try:
            get =  CustomUser.objects.get(username=username)
            return get
        except CustomUser.DoesNotExist:
            return None 
    @database_sync_to_async
    def get_post(self,postid):
        try:
            get =  Posts.objects.get(id=postid)
            print(get)
            return get
        except Posts.DoesNotExist:
            return None
    
    @database_sync_to_async
    def create_Notification(self,user,sender,content,post):
        # creer  la notif puis la sauvegarde avec les trucs aproprie
        new_notification= Notification.objects.create(user=user,sender=sender,content=content,post=post)
        new_notification.save()
        return NotificationSerializer(new_notification,many=False).data

class VideoCallConsumer(AsyncWebsocketConsumer):
        
    async def connect(self):
        # get the room name from url
        self.room_name=self.scope['url_route']['kwargs']['room_name']
        self.room_group_name=f'video_call_{self.room_name}'
    # getting the actual room name
    
        self.room=await self.get_room()
        if self.room:
            await self.channel_layer.group_add(self.room_group_name,self.channel_name)
            await self.accept()
        else:
            await  self.close()


    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_group_name,self.channel_name)

        # when receive data from socket client
    async def receive(self, text_data):
        data= json.loads(text_data)
        action = data.get('action')
        if action=='offer':
            await self.channel_layer.group_send(
                self.room_group_name,{
                    'type':'send_offer',
                    'offer':data['offer'],
                    'from':data['from']
                }
            )
        elif action =='answer':
            await self.channel_layer.group_send(
                self.room_group_name,{
                    'type':'send_answer',
                    'offer':data['answer'],
                    'to':data['to']
                }
            
        )
        elif action=='ice-candidate':
            await self.channel_layer.group_send(
                self.room_group_name,{
                    'type':'send_ice_candidate',
                    'candidate':data['candidate'],
                    'from':data['from']
                }
            )

    
    async def send_offer(self,event):
        await self.send(text_data=json.dumps({
            'type':'offer',
            'offer':event['offer'],
            'from':event['from']
        }))
    async def send_answer(self,event):
        await self.send(text_data=json.dumps({
            'type':'answer',
            'answer':event['answer'],
            'to':event['to']
        }))
    async def send_ice_candidate(self,event):
        await self.send(text_data=json.dumps({
            'type':'ice-candidate',
            'candidate':event['candidate'],
            'from':event['from']
        }))
    
    
    
    
    
    @database_sync_to_async
    def get_room(self):
        try:
            get =  Room.objects.get(room_name=self.room_name)
            return get
        except Room.DoesNotExist:
            return None