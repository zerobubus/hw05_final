from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        
        model = Post
        fields = ['group', 'text', 'image']
        labels = {
            'group': "Группа",
            'text': "Текст"
        }
        help_texts = {
            'group': "Выберите группу для поста(необязательно)",
            'text': "Введите текст"
        }


class CommentForm(forms.ModelForm):
    
    class Meta:
        model = Comment
        fields = ['text']
        labels = {
            'text': "Текст"
        }
        help_texts = {
            'text': "Введите текст"
        }       

   
