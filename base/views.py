from rest_framework.decorators import api_view,parser_classes,permission_classes
# from django.contrib.auth.models import User
from rest_framework.generics import CreateAPIView,RetrieveAPIView
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication,BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import Posts,Like,Commentaire,ImagePublication,Amis,CustomUser,Request,Follow,SavedPost
from .serializers import PostsSerializer,LikeSerializer,CommentaireSerializer,ImagePublicationSerializer,AmisSerializer,UserSerializer,UserSerialize,CreateUserSerializer,RequestSerializer,UserFollower,UserS
from . import serializers
from rest_framework.parsers import MultiPartParser,FormParser
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from django.db.models import Q
from ChatApp.models import Room,Message,Notification

# test

from rest_framework.permissions import AllowAny
from rest_framework import status
# test
class LoginView(APIView):
    authentication_classes=[TokenAuthentication]
    def post(self,request):
        # print(request.data)
        user= authenticate(username=request.data['username'],password=request.data['password'])
        if user:
            token , created= Token.objects.get_or_create(user=user)
            return Response ({'token':token.key})
        else :
            return Response({'error':"invalid credential"},status=400)

class CreateUserAPIView(CreateAPIView):
    serializer_class = CreateUserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        # We create a token than will be used for future auth
        token = Token.objects.create(user=serializer.instance)
        token_data = {"token": token.key}
        return Response(
            {**serializer.data, **token_data},
            status=200,
            headers=headers
        )


class LogoutUserAPIView(APIView):
    queryset = CustomUser.objects.all()

    def get(self, request, format=None):
        # simply delete the token to force a login
        request.user.auth_token.delete()
        return Response(status=200)

class PostUpload(APIView):
    queryset= Posts.objects.all()
    parser_classes=(MultiPartParser,FormParser)
    serializer_class= PostsSerializer
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsAuthenticated]

    def post(self,request,*args,** kwargs):
        image= request.FILES.get("image")
        print(image)
        description= request.data['description']
        Posts.objects.create(description=description,image=image,utilisateur=request.user)
        
        return Response("Reussi",status=200)

class CommentUpload(APIView):
    queryset= Commentaire.objects.all()
    parser_classes=(MultiPartParser,FormParser)
    serializer_class= CommentaireSerializer
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsAuthenticated]

    def post(self,request,*args,** kwargs):
        image= request.data["image"]
        description= request.data['description']
        Commentaire.objects.create(description=description,image=image)
        return Response("Reussi",status=200)

@api_view(['GET'])
def getAllUser(request):
    try:
        user = CustomUser.objects.all()
        serializer = UserFollower(user, many=True,context={'request':request})
        return Response(serializer.data)
    except Exception as e:
        print(e)
        return Response("error",status=400)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getSingle(request,pk):
    try: 
        user = CustomUser.objects.filter(username=pk)
        print(user[0])
        serializer = UserSerializer(user[0], many=False)
        return Response(serializer.data,status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response("error",status=400)


@api_view(['POST'])
def userRegister(request):
    try:
        if request.method=="POST":
            username=request.data.get('username')
            password=request.data.get('password')
            email=request.data.get('email')
            print(username,password,email)
            try:
                return
            except Exception as e:
                print(e)
            user= CustomUser.objects.create_user(username=username,email=email,password=password)
            token = Token.objects.create(user=user)

            token_data = {"token": token.key}
            print(token,token_data)
            user.save()
            return Response("oui",status=200)
    except Exception as e:
        print(e)        
        return Response("Non",status=400)

@api_view(['POST'])
def logUser(request):
    if request.method == 'POST':
        print(request)
        username = request.data.get('username')
        password = request.data.get('password')
        print(username,password)
        try:
            user = CustomUser.objects.filter(username=username,password=password)
        except Exception as e:
            print(e)
            return Response("Erreur",status=400)
        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            usero= UserSerialize(user,many=False)
            print(request)
            content={
                'user':str(request.user),
                'auth':(request.auth)
            }
            print(content)
            return Response(content,status=200)
        else:
            return Response("utilisateur non existant",status=400)


@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def getPosts(request):        
    print(request.user)
    try:
        post = Posts.objects.select_related('utilisateur').all()
        serializer = PostsSerializer(post, many=True,context={'request':request})
        return Response(serializer.data,status=200)
    except Exception as e:
        print (e)
        return Response("Erreur",status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getPost(request,pk):
    try:
        print(pk)
        post = Posts.objects.filter(id=pk)
        if post:
            serializer = PostsSerializer(post, many=True,context={'request':request})
            print(post)
        return Response(serializer.data,status=200)
    except Exception as e:
        print(e)
        return Response('eror',status=400)
@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def likeAction(request,pk):
    print(request.user)
    if request.method=='POST':
        post = Posts.objects.get(id=pk)
        like= Like.objects.filter(user=request.user,postId=post)

        if like.exists():
            post.nombre_like= post.nombre_like-1
            like.delete()
            post.save()
            return Response({"nombre_like":post.nombre_like,"liked":False,'notification':None},status=200)
        else :
            post.nombre_like = post.nombre_like+1
            like= Like.objects.create(user=request.user,postId=post)
            like.save()
            post.save()

            # creer la notification maintenant pour l'envoyer au post owner

            # notif= Notification.objects.get()
            
            return Response({"nombre_like":post.nombre_like,"liked":True,},status=200)

@api_view(['GET'])
def getCommentaires(request):
    commentaire = Commentaire.objects.all()
    serializer = CommentaireSerializer(commentaire, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getCommentaire(request,pk):
    commentaire = Commentaire.objects.filter(post=pk)
    serializer = CommentaireSerializer(commentaire, many=True)
    return Response(serializer.data)


@api_view(['POST','GET'])
@parser_classes([MultiPartParser,FormParser])
@permission_classes([IsAuthenticated])
def setCommentaire(request, pk):
    contenue = request.data["textComment"]
    image= request.FILES.get('image')
    try:
        post = Posts.objects.get(id=pk)
        commentaire = Commentaire.objects.create(post=post,utilisateur=request.user, contenue=contenue,image=image)
        commentaire.save()
        comment = Commentaire.objects.filter(post=pk)
        serializer = CommentaireSerializer(comment, many=True)
        return Response(serializer.data,status=200)
    except Posts.DoesNotExist:
        return Response("Post not found", status=404)



 
@api_view(['POST','GET'])
@permission_classes([IsAuthenticated])
def getProfileUser(request,pk):
    try:
        user= CustomUser.objects.get(username=pk)
        follower= Follow.objects.filter(user=user)
        following= Follow.objects.filter(follower=user)
        isTheconnected= (user==request.user)
        post= Posts.objects.filter(utilisateur=user)
        serialize= UserSerializer(user,many=False)

        return Response({"user":serialize.data,"follower":len(follower),"isTheConnected":isTheconnected,"nombrePost":len(post),"following":len(following)},status=200)

    except Exception as e:
        print(e)
        return Response("error",status=400)

@api_view(['POST','GET'])
@permission_classes([IsAuthenticated])
def getUserPost(request,pk):
    try:
        print(request.user)
        user= CustomUser.objects.get(username=pk)
        post= Posts.objects.filter(utilisateur=user)
        serializer= PostsSerializer(post,many=True,context={"request":request}) 
        # print(serializer.data)
        return Response(serializer.data,status=200)
        # return Response("oui",status=200)

    except Exception as e:
        print(e)
        return Response("error",status=400)    


@api_view(['GET','POST'])
@parser_classes([MultiPartParser,FormParser])
def changemenProfile(request,username):
    image= request.FILES.get('image')
    try:
        user= CustomUser.objects.get(username=username)
        
        user.avatar=image
        user.save()
        serializer=UserSerializer(user,many=False)
        return Response(serializer.data,status=200)
    except Exception as e:
         print(e)
         Response("Erreur not found", status=404)


@api_view(['GET','POST'])

def changemenBio(request,username):    
    try:
        user= CustomUser.objects.get(username=username)
        
        user.bio=request.POST.get('bio')
        
        user.save()
        serializer=UserSerializer(user,many=False)
        return Response(serializer.data,status=200)
    except Exception as e:
         print(e)
         Response("Erreur not found", status=404)

@api_view(['GET','POST'])
def allFriend(request,username):
    user= CustomUser.objects.get(username=username)
    amis= Amis.objects.filter(Q(user1=user)|Q(user2=user))
    serialize= AmisSerializer(amis,many=True)
    return Response(serialize.data,status=200)

@api_view(['GET','POST']) 
def allFriendRequest(request,username):
    try:
        user= CustomUser.objects.get(username=username)
        followers=Follow.objects.filter(user=user).values_list('follower',flat=True)
        following=Follow.objects.filter(follower=user).values_list('user',flat=True)
        not_followed_back = CustomUser.objects.filter(id__in=followers).exclude(id__in=following)
        serializer = UserS(not_followed_back, many=True,context={"request":request})
        return Response(serializer.data)
    except Exception as e:
        print(e)
        return Response("error",status=400)
@api_view(['GET','POST'])
def sendRequest(request,username):
    try:
        if request.method=="POST":
            # print(request.data['receivername'])
            user= CustomUser.objects.get(username=username)
            receivername= request.data["receivername"]
            receiver= CustomUser.objects.get(username=receivername)
            f= Request.objects.filter(Q(sender=user)|Q(receiver=user))
            friendRequest= Request.objects.create(sender=user,receiver=receiver)
            friendRequest.save()
            serializers=RequestSerializer(friendRequest,many=False)
            return Response(serializers.data,status=200)
        return Response("oui",status=200)
    except Exception as e:
        print(e)
        return Response("erreur",status=400)
    

@api_view(['GET','POST'])
def acceptrequest(request,pk):
    try:
        if request.method=="POST":
            friendRequest= Request.objects.get(id=pk)
            user=friendRequest.receiver
            receiver= friendRequest.sender
            friendRequest.delete()
            # creation d'amis
            amis= Amis.objects.create(user1=user,user2=user)
            amis.save()
            # creation de room
            room= Room.objects.create(user1=user,user2=receiver)
            room.save()
            
            return Response(status=200)
    except Exception as e:
        return Response("erreur",status=400)


@api_view(['GET','POST'])
def rejectrequest(request,pk):
    try:
        if request.method=="POST":
            friendRequest= Request.objects.get(id=pk)
            friendRequest.delete()
            return Response(status=200)
    except Exception as e:
        return Response("erreur",status=400)
    

@api_view(['GET','POST'])
def Search(request,username):
    try:
            searchValue= request.POST.get('searchValue')
            user= CustomUser.objects.get(username=username)
            amis= Amis.objects.filter(Q(user1=user)|Q(user2=user))
            alluser=CustomUser.objects.filter(Q(username__icontains=searchValue))
            friendRequest= Request.objects.filter(Q(sender=user)|Q(receiver=user))
            reste=[]
            for use in alluser:
                if use not in amis and use != user and use not in friendRequest:
                    reste.append(use)
                    
            serializer = UserFollower(reste,many=True)
            return Response(serializer.data,status=200)
    except Exception as e:
        return Response("erreur",status=400)


@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def SearchAll(request,searchvalue):
    try:
            alluser=CustomUser.objects.filter(Q(username__icontains=searchvalue))
            allposts= Posts.objects.filter(Q(description__icontains=searchvalue))
            serializer = UserFollower(alluser,many=True,context={'request':request})
            posetSerializer= PostsSerializer(allposts,many=True,context={'request':request})
            return Response({"dataUser":serializer.data,"dataPost":posetSerializer.data},status=200)
    except Exception as e:
        print(e)
        return Response("erreur",status=400)


@api_view(['GET','POST'])
def nonFi(request,username):
    try:
            user= CustomUser.objects.get(username=username)
            amis= Amis.objects.filter(Q(user1=user)|Q(user2=user))
            friend_request= Request.objects.all()
            alluser=CustomUser.objects.all()
            reste=[]
            reste1=[]
            for use in alluser:
                if use not in amis:
                    if use!=user:   
                        reste.append(use)    
            for use1 in alluser:
                if use1 not in friend_request:
                    if use1!=user:   
                        reste1.append(use1)   
            # vrai=[v for v in reste1]
            lesDeux=[]
            for v in reste:
                if v in reste1:
                    lesDeux.append(v)
            serializer = UserSerializer(lesDeux,many=True)
            
            print(serializer.data)
            return Response(serializer.data,status=200)
            
    except Exception as e:
        print(e)
        return Response("erreur",status=400)
    


@api_view(['GET','POST'])
def follow(request,username):
    try:
        if request.method == 'POST':
            use = request.data['user']
            user=CustomUser.objects.get(username=use)
            follower=  CustomUser.objects.get(username=username)
            if Follow.objects.filter(follower=follower, user=user).first():
                delete_follower = Follow.objects.get(follower=follower, user=user)
                delete_follower.delete()
                return Response({False},status=200)

            else:
                new_follower = Follow.objects.create(follower=follower, user=user)
                ifroom= Room.objects.filter(Q(user1=user,user2=follower)|Q(user1=follower,user2=user)).exists()
                if not ifroom:
                    room=Room.objects.create(user1=user,user2=follower)
                    room.save() 
                new_follower.save()
                return Response({True},status=200)
    except Exception as e:
        print(e)
        return Response("Error",status=400)


@api_view(['GET','POST'])
# @permission_classes([IsAuthenticated])
def getNonFollowed(request,username):
    try:
        user= CustomUser.objects.get(username=username)
        followed=Follow.objects.filter(follower=user).values_list('user',flat=True)
        not_following = CustomUser.objects.exclude(id__in=followed).exclude(id=user.id)
        serializer = UserS(not_following, many=True,context={"request":request})
        return Response(serializer.data)
    except Exception as e:
        print(e)
        return Response("error",status=400)

@api_view(['GET','POST'])
def savedPost(request,username):
    print(request.user)
    try:
        user= CustomUser.objects.get(username=username)
        # post = Posts.objects.select_related('utilisateur').filter(utilisateur=user)
        saved= SavedPost.objects.filter(user=user)
        post=[sa.post for sa in saved]
        serializer = PostsSerializer(post, many=True,context={'request':request})
        return Response(serializer.data,status=200)
    except Exception as e:
        print (e)
        return Response("Erreur",status=400)
    
@api_view(['GET','POST'])
def savePost(request,username):
 if request.method=='POST':
        post=Posts.objects.get(id=request.data['postId'])
        sav = SavedPost.objects.filter(user=request.user,post=post)
        if sav.exists():
            sav.delete()
            return Response({"saved":False},status=200)
        else :
            sav= SavedPost.objects.create(user=request.user,post=post)
            sav.save()
            return Response({"saved":True},status=200)


    
@api_view(['GET','POST'])
def deletePost(request,pk):
    try:
        if request.method=='POST':
            post=Posts.objects.get(id=pk)
            post.delete()
            return Response("Oui",status=200)
    except Exception as e:
        print(e)
        return Response('non',status=400)