from django.contrib import admin
from .models import Post, Group, Comment


class PostAdmin(admin.ModelAdmin):
    
    list_display = ("pk", "text", "pub_date", "author") 
    search_fields = ("text",) 
    list_filter = ("pub_date",) 
    empty_value_display = "-пусто-"


class GroupAdmin(admin.ModelAdmin):
    
    list_display = ("title", "description", "slug") 
    search_fields = ("title",) 


class CommentAdmin(admin.ModelAdmin):
    
    list_display = ("post", "text", "created", "author") 
    search_fields = ("post",) 
    


admin.site.register(Group, GroupAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
