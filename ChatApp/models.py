from django.db import models
from base.models import CustomUser,Posts
import uuid
# Create your models here.
class Room(models.Model):
    room_name=models.UUIDField(default=uuid.uuid4,editable=False,unique=True)
    user1= models.ForeignKey(CustomUser,related_name='user1_room',on_delete=models.CASCADE,null=True,blank=True)
    user2= models.ForeignKey(CustomUser,related_name='user2_room',on_delete=models.CASCADE,null=True,blank=True)
    updated = models.DateTimeField(auto_now=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)

    class Meta:
        ordering = ['-updated', '-created_at']

    def __str__(self):
        return f'Room: {self.room_name} {self.user1} and {self.user2}'
    
class Message(models.Model):
    
    room= models.ForeignKey(Room,on_delete=models.CASCADE,null=True,blank=True)
    
    sender= models.ForeignKey(CustomUser,related_name='sender_message',on_delete=models.SET_NULL,null=True)
    
    content= models.TextField(blank=True,null=True)

    image= models.ImageField(upload_to='image/message_image/',null=True,blank=True)

    video=models.FileField(upload_to='video/message_video',null=True,blank=True)

    audio = models.FileField(upload_to='audio/message_audio',null=True,blank=True)
    
    is_read=models.BooleanField(default=False)
    
    timestamp= models.DateTimeField(auto_now_add=True,null=True)

    
    def __str__(self):
        if(self.audio):
            return  f'[user 1] : {self.room.user1} [user 2] : {self.room.user2} [audio]: {self.audio}'
        if(self.video):
            return f'[user 1] : {self.room.user1} [user 2] : {self.room.user2} [video]:{self.video}'
    
        if(self.content):
            return f'[user 1] : {self.room.user1} [user 2] : {self.room.user2} [content]: {self.content[0:10]} '
        if(self.image):
            return f'[user 1] : {self.room.user1} [user 2] : {self.room.user2} image:{self.image}'
    

    # Room: 8d2d4385-2857-4f80-99b2-40e0b67d828b 
class Notification(models.Model):
    user=models.ForeignKey(CustomUser,related_name='notif_user',on_delete=models.CASCADE)
    sender=models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True)
    post= models.ForeignKey(Posts,related_name='notif_post',on_delete=models.CASCADE,null=True)
    content= models.TextField()
    type=models.CharField(default='like',max_length=11)
    is_read=models.BooleanField(default=False)
    created_at= models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.user.username