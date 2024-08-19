from django.db import models

from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    email=models.EmailField(blank=False,null=False)
    name= models.CharField(blank=True,null=True,max_length=200)
    bio= models.CharField(max_length=200,blank=True,null=True)
    
    avatar = models.ImageField(upload_to='images/',default='default.png',null=True,blank=True)
    def __str__(self):
        return self.username

class Posts(models.Model):
    utilisateur= models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True) 
    description= models.TextField(null=True,blank=True)
    image = models.ImageField(upload_to='images/',default=None,null=True,blank=True)
    nombre_like= models.IntegerField(default=0)
    created  = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now= True)
    def __str__(self) :
        return str(self.id)
    class Meta:
       ordering = ['-updated', '-created']


class Commentaire(models.Model):
    utilisateur= models.ForeignKey(CustomUser,related_name='utilisateur',on_delete=models.CASCADE,null=True) 
    contenue = models.CharField(max_length=500)
    post = models.ForeignKey(Posts,related_name='post',on_delete=models.CASCADE)
    image= models.ImageField(upload_to='images/commentaire',default=None,null=True,blank=True)
    created= models.DateTimeField(auto_now_add=True,blank=True,null=True)

    def __str__(self):
        return str(self.id)
 
class ImagePublication(models.Model):
    posts=models.ForeignKey(Posts,related_name='posts',on_delete=models.CASCADE)
    photo=models.ImageField(upload_to='images/image_de_publication/')
    def __str__(self):
        return str(self.id)

class Like(models.Model):
    user= models.ForeignKey(CustomUser,null=True,related_name='likeur',on_delete=models.CASCADE)
    postId= models.ForeignKey(Posts,null=True,related_name='postss',on_delete=models.CASCADE)
    def __str__(self) :
        return str(self.id)

class Amis(models.Model):
    user1= models.ForeignKey(CustomUser,related_name='amis1',null=True,on_delete=models.CASCADE) 
    user2= models.ForeignKey(CustomUser,related_name='amis2',null=True,on_delete=models.CASCADE) 
    def __str__(self) :
        return str(self.id)
    
class Request(models.Model):
    sender= models.ForeignKey(CustomUser,related_name='senderequest',null=True,on_delete=models.CASCADE) 
    receiver= models.ForeignKey(CustomUser,related_name='receiverequest',null=True,on_delete=models.CASCADE) 
    timestamp=models.DateTimeField(auto_now=True)
    def __str__(self) :
        return f'ID = {str(self.id)}  sender = {self.sender.username} receiver = {self.receiver.username}'
    
class Follow(models.Model):
    user= models.ForeignKey(CustomUser,related_name='user_follow',null=True,on_delete=models.CASCADE) 
    follower= models.ForeignKey(CustomUser,related_name='follower',null=True,on_delete=models.CASCADE) 
    # timestamp=models.DateTimeField(auto_now=True)
    def __str__(self) :
        return f'ID = {str(self.id)}  user = {self.user.username} follower = {self.follower.username}'
    

class SavedPost(models.Model):
    
    user= models.ForeignKey(CustomUser,related_name='saver',null=True,on_delete=models.CASCADE) 
    post= models.ForeignKey(Posts,null=True,related_name='postsse',on_delete=models.CASCADE)
    date= models.DateTimeField(auto_now=True,null=True)
    
    def __str__(self):
        return f"{self.user.username} : {self.post}"