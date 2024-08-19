from cProfile import Profile
from rest_framework.serializers import ModelSerializer,CharField,SerializerMethodField
# from django.contrib.auth.models import User
from .models import Posts,Like,Commentaire,ImagePublication,Amis,CustomUser,Request,Follow,SavedPost

from django.db.models import Q
# test ity


class CreateUserSerializer(ModelSerializer):
    username = CharField()
    password = CharField(write_only=True,
                                     style={'input_type': 'password'})

    class Meta:
        model = CustomUser
        fields = ['id','username','email','avatar','bio','name','password'] 
        write_only_fields = ('password')

    def create(self, validated_data):
        user = super(CreateUserSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user



# farany test



class UserFollower(ModelSerializer):
    
    followed= SerializerMethodField() 
    class Meta:
        model= CustomUser
        fields = ['id','username','email','avatar','bio','name','password','followed']

    def get_followed(self,obj):
        user= self.context['request'].user
        return Follow.objects.filter(follower=obj,user=user).exists()
    
class UserFollow(ModelSerializer):
    
    followed= SerializerMethodField() 
    class Meta:
        model= CustomUser
        fields = ['id','username','email','avatar','bio','name','password','followed']

    def get_followed(self,obj):
        user= self.context['request'].user
        return Follow.objects.filter(user=obj,follower=user).exists()
       
class UserSerialize(ModelSerializer):
    class Meta:
        model=CustomUser
        fields = ['id','username','email','avatar','bio','name','password']

    def create(self, validated_data):
        user = super(UserSerialize, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user
    
class UserSerializer(ModelSerializer):
    class Meta:
        model= CustomUser
        fields = ['id','username','email','avatar','bio','name','password']

    def get_liked(self,obj):
        user= self.context['request'].user
        return Like.objects.filter(postId=obj,user=user).exists()
    

class PostsSerializer(ModelSerializer):
    utilisateur=UserFollow()
    liked= SerializerMethodField()
    saved=SerializerMethodField()
    class Meta:
        model = Posts
        fields = ['id','utilisateur','description','created','nombre_like','image','liked','saved']

    def get_liked(self,obj):
        user= self.context['request'].user
        return Like.objects.filter(postId=obj,user=user).exists()
    def get_saved(self,obj):
        user= self.context['request'].user
        return SavedPost.objects.filter(post=obj,user=user).exists()


    
class SinglePostsSerializer(ModelSerializer):
    utilisateur=UserSerializer()
    liked= SerializerMethodField()
    class Meta:
        model = Posts
        fields = ['id','utilisateur','description','created','nombre_like','image','liked']

    def get_liked(self,obj):
        user= self.context['request'].user
        return Like.objects.filter(postId=obj,user=user).exists()



class LikeSerializer(ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'

class CommentaireSerializer(ModelSerializer):
    utilisateur= UserSerialize()
    class Meta:
        model = Commentaire
        fields = '__all__'

class AmisSerializer(ModelSerializer):
    user1=UserSerializer()
    user2=UserSerializer()

    class Meta:
        model = Amis
        fields = '__all__'




class RequestSerializer(ModelSerializer):
    sender=UserSerializer()
    receiver=UserSerializer()

    class Meta:
        model = Request
        fields = '__all__'

class ImagePublicationSerializer(ModelSerializer):
    class Meta:
        model = ImagePublication
        fields = '__all__'

# class UserProfileSerializer(ModelSerializer):
#     nombre_amis=SerializerMethodField()
#     istheConnected= SerializerMethodField()
#     class Meta:
#         model= CustomUser
#         fields = ['id','username','email','avatar','bio','name','nombre_amis']
#     def get_nombre_amis(self,obj):
#         user= self.context['request'].user
#         amis= Amis.objects.filter(
#         Q(user1=user) |
#         Q(user2=user)
#         )
#         return len(amis) 
    
#     def get_istheConnected(self):
#         user= self.context['request'].user
#         amis= Amis.objects.filter(
#         Q(user1=user) |
#         Q(user2=user)
#         )
#         return len(amis) 
        
  
class UserS(ModelSerializer):
    class Meta:
        model= CustomUser
        fields = ['id','username','email','avatar','bio','name']

class FollowSerializer(ModelSerializer):
    user=UserS()
    follower=UserS()
    class Meta:
        model=Follow
        fields=['id','user','follower']
