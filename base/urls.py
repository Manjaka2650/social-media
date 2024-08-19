from django.http import HttpResponse
from django.shortcuts import render
from django.urls import path
from . import views
from ChatApp.models import Message
from rest_framework.authtoken.views import obtain_auth_token
def home(request):

    mess= Message.objects.all()

    return render(request,'ChatApp/index.html',{'mess':mess})
urlpatterns = [
    path('',home),    

    path('posts/',views.getPosts,name='getPosts'),

    path('post/<str:pk>/',views.getPost,name='getPost'),

    path('likeAction/<str:pk>',views.likeAction,name='likeAction'),

    path('commentaire/',views.getCommentaires,name='getCommentaire'),

    path('commentaire/<str:pk>',views.getCommentaire,name='getCommentaire'),

    path('setCommentaire/<str:pk>',views.setCommentaire,name='setCommentaire'),

    path('new-post/',views.PostUpload.as_view(),name='new-post'),

    # path('register/',views.UserCreateApiView.as_view(),name='register'),

    path('user/',views.getAllUser,name='user'),

    path('profileUser/<str:pk>',views.getProfileUser,name='profile-user'),

    path('postUser/<str:pk>',views.getUserPost,name='post-user'),


    path('user/<str:pk>',views.getSingle,name='user-detail'),

    # path('userInfo/',views.userInfo,name='userInfo'),

    # path('login/',views.logUser,name='login')
    path('login/',views.LoginView.as_view(),name='auth_user_login'),

    path('auth/register/',views.CreateUserAPIView.as_view(),name='auth_user_create'),

    path('change-profile-image/<str:username>',views.changemenProfile,name='change-profile-image'),

    path('change-bio/<str:username>',views.changemenBio,name='change-bio'),

    path("all-friend/<str:username>",views.allFriend,name="all-friend") ,

    path("all-non-friend/<str:username>",views.nonFi,name="all-non-friend"),
    
    path("all-friend-request/<str:username>",views.allFriendRequest,name="all-friend-request"),

    path('send-request/<str:username>',views.sendRequest,name='send-request'),

    path('accept-friend-request/<str:pk>',views.acceptrequest,name='accept-request'),

    path('reject-friend-request/<str:pk>',views.rejectrequest,name='reject-request'),

    path('search-friend/<str:username>',views.Search,name='search-friend'),
    
    path('search/<str:searchvalue>',views.SearchAll,name='search'),

    path('follow-action-friend/<str:username>',views.follow,name='follow-action-friend'),

    path('non-followed-user/<str:username>',views.getNonFollowed,name='non-followed-user'),

    path('saved-post/<str:username>',views.savedPost,name='saved-post'),

    path('save-post/<str:username>',views.savePost,name='saved-post'),

    path('delete-post/<str:pk>',views.deletePost,name='  delete-post'),

  
]



