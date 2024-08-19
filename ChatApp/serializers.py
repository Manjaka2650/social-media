from rest_framework.serializers import ModelSerializer,CharField,SerializerMethodField
# from django.contrib.auth.models import User
from .models import Message,Room,Notification
from base.models import CustomUser
from django.db.models import Q

    
class UserSerializer(ModelSerializer):
    class Meta:
        model= CustomUser
        fields = ['id','username','avatar','name']



class MessageSerializer(ModelSerializer):
    sender=UserSerializer()
    # image_url=SerializerMethodField()
    class Meta:
        model= Message
        fields = ['id','sender','room','content','timestamp','image','video','audio','is_read']
    # def get_image_url(self,obj):
    #     if obj.image:
    #         return obj.image.url
    #     return None

class RoomSerializers(ModelSerializer):
    # user1=UserSerializer()
    # user2=UserSerializer()
    last_message=SerializerMethodField()
    other_user=SerializerMethodField()
    class Meta:
        model=Room
        fields=['id','room_name','other_user','last_message']

    def get_last_message(self,obj):
        l= Message.objects.filter(room=obj).order_by('-timestamp').first()
        return MessageSerializer(l).data if l else None
    def get_other_user(self,obj):
        request_user=self.context['request'].user
        if obj.user1==request_user:
            return UserSerializer(obj.user2).data
        return UserSerializer(obj.user1).data


class NotificationSerializer(ModelSerializer):
    sender=UserSerializer()
    user=UserSerializer()
    class Meta:
        model= Notification
        fields = '__all__'