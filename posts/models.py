from django.db import models 
from django.contrib.auth import get_user_model 
 
User = get_user_model() 
 
 
class Group(models.Model): 
    title = models.CharField(max_length=200, verbose_name="название") 
    description = models.TextField(max_length=100, verbose_name="описание") 
    slug = models.SlugField(unique=True,)  
 
    def __str__(self): 
        return self.title       
 
 
class Post(models.Model): 
    text = models.TextField(verbose_name="текст") 
    pub_date = models.DateTimeField("date published", auto_now_add=True) 

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, 
        related_name="authors", 
        verbose_name="автор"
    ) 
    group = models.ForeignKey(
        Group, on_delete=models.SET_NULL, 
        related_name="posts", 
        blank=True, null=True,
        verbose_name="группа"
    ) 
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    class Meta: 
        ordering = ["-pub_date"] 
     
    def __str__(self): 
        return self.text   


class Comment(models.Model): 
    
    post = models.ForeignKey(
        Post, on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='comments'
        )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
        )
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ('created',)

class Follow(models.Model): 
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower"
        )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following"
        )
   
    