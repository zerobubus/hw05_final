import io
import tempfile
from PIL import Image
from django.test import TestCase 
from django.test import Client 
from .models import Post, Group, User, Follow 
from django.urls import reverse 
from django.core.cache import cache 
from django.conf import settings 
from django.core.files.base import ContentFile
from django.test import override_settings
 
 
class Test(TestCase): 
 
    def setUp(self): 
         
        self.user = User.objects.create_user( 
            username="Kostya",  
            email="1ka@mail.com",  
            password="12345" 
        ) 
 
        self.user1 = User.objects.create_user( 
            username="Anna",  
            email="anna@mail.com",  
            password="67890" 
        ) 
        self.client_auth = Client() 
        self.client_auth.force_login(self.user) 
        self.client_auth2 = Client() 
        self.client_auth2.force_login(self.user1) 
         
        self.post = Post.objects.create(text="test", author=self.user) 
        self.group = Group.objects.create( 
            title="linkin_park", 
            slug="linkin_park" 
        ) 
        self.urls_for_created_post = {"index":reverse("index"),    
            "profile":reverse("profile", kwargs={"username": self.post.author}),   
            "post":reverse("post",kwargs={"username": self.post.author,"post_id": 2})   
        }           
         
    def test_profile(self): 
        response = self.client.get( 
            reverse( 
                "profile",  
                kwargs=dict(username=self.user.username) 
        )) 
        self.assertEqual(response.status_code, 200) 
         
 
    def test_new_post_authorized(self): 
        
        response = self.client_auth.post( 
            reverse("new_post"), 
            data={ 
                "text": "тест тест", 
                "group": self.group.id 
            } 
        ) 
 
        post = Post.objects.first() 
        self.assertEqual(response.status_code, 302) 
        self.assertEqual(Post.objects.count(), 2) 
        self.assertEqual(post.author, self.user) 
        self.assertEqual(post.text, "тест тест") 
        self.assertEqual(post.group, self.group) 
 
    def test_new_post_not_authorized(self): 
         
        response = self.client.post( 
            reverse("new_post"), 
            { 
                "text": "тест тест", 
                "group": self.group, 
            } 
        ) 
        post = Post.objects.first() 
        login = reverse("login") 
        new = reverse("new_post") 
        self.assertEqual(response.status_code, 302)   
        self.assertRedirects(response, f"{login}?next={new}")   
        self.assertEqual(Post.objects.count(), 1) 
        

    
    def check_post_on_page(self, url, text, author, group): 
        
        response = self.client_auth.get(url) 
        if "paginator" in response.context: 
            post_list = response.context["paginator"].object_list[0] 
        else: 
            post_list = response.context["post"] 
         
        self.assertEqual(post_list.author, author) 
        self.assertEqual(post_list.text, text) 
        self.assertEqual(post_list.group, group) 
        
    
    def test_post_on_pages(self): 
        cache.clear()  
        response = Post.objects.create(text="PPPPPPPPPPP", author=self.user, group = self.group) 
        post = Post.objects.first() 
        self.assertEqual(Post.objects.count(), 2) 
        text = post.text 
        author = post.author 
        group = post.group 
         
        for url in self.urls_for_created_post.values(): 
            self.check_post_on_page(url, text, author, group)  
        
    
    def test_post_edit(self): 
        cache.clear()  
        post = Post.objects.create(text="test text", 
                                   author=self.user) 
        edit_group = Group.objects.create(title="edit_group", 
                                          slug="edit_group") 
        response = self.client_auth.post( 
            reverse("post_edit", kwargs= 
                    {"username": post.author.username, 
                     "post_id": post.id}), 
            {"text": "edit text", "group": edit_group.id}, follow=True) 
        post = Post.objects.get(id=post.id) 
        text = post.text 
        author = post.author 
        group = post.group 
        for url in self.urls_for_created_post.values(): 
            self.check_post_on_page(url, text, author, group) 
 
    def test_404(self): 
         
        response = self.client_auth.get("not_exist_url/") 
        self.assertEqual(response.status_code, 404) 
 
    def create_post_with_img(self): 
        with tempfile.TemporaryDirectory() as temp_directory:
            with override_settings(MEDIA_ROOT=temp_directory):
                byte_image = io.BytesIO()
                im = Image.new("RGB", size=(500, 500), color=(255, 0, 0, 0))
                im.save(byte_image, format='jpeg')
                byte_image.seek(0)
                img = ContentFile(byte_image.read(), name='test.jpeg') 
                response = self.client_auth.post( 
                    reverse("new_post"), 
                    {"text": "post with image", 
                    "group": self.group.id, 
                    "image": img}, follow=True) 
    
    def create_post_with_no_img(self): 
        with tempfile.TemporaryDirectory() as temp_directory:
            with override_settings(MEDIA_ROOT=temp_directory):
                byte_image = io.BytesIO()
                im = Image.new("RGB", size=(500, 500), color=(255, 0, 0, 0))
                im.save(byte_image, format='jpeg')
                byte_image.seek(0)
                img = ContentFile(byte_image.read(), name='test.txt') 
                response = self.client_auth.post( 
                    reverse("new_post"), 
                    {"text": "post with image", 
                    "group": self.group.id, 
                    "image": img}, follow=True) 
                                             
    def test_img_post(self): 
        
        self.create_post_with_img() 
        post = Post.objects.first() 
        response = self.client_auth.get( 
            reverse("post", kwargs={"username": post.author.username, 
                                    "post_id": post.id})) 
        self.assertContains(response, "img")  
        
 
    def test_img_on_pages(self): 
        cache.clear()  
        self.create_post_with_img() 
        
        for url in self.urls_for_created_post.values(): 
            response = self.client_auth.get(url) 
            self.assertContains(response, 'img') 
            self.assertEqual(Post.objects.count(), 2) 
     
    def test_not_img_upload(self): 
        cache.clear() 
        self.create_post_with_no_img() 
                           
        self.assertEqual(Post.objects.count(), 1) 
 
    def test_cache(self): 
         
        self.client_auth.post( 
        reverse("new_post"), 
        data={ 
            "text": "test test", 
            "group": self.group.id 
        }, 
        follow=True 
    ) 
        response = self.client_auth.get(reverse("index")) 
        self.assertContains(response, "test test") 
 
        self.client_auth.post( 
        reverse("new_post"), 
        data={ 
            "text": "test cache", 
            "group": self.group.id 
        }, 
        follow=True 
    ) 
        response = self.client_auth.get(reverse("index")) 
        self.assertNotContains(response, "test cache") 
 
    def test_follow(self): 
 
        follow = Follow.objects.create(user=self.user, author=self.user1) 
        following = Follow.objects.filter(user=self.user) 
        self.assertEqual(following.count(), 1) 
        un_follow = Follow.objects.filter(user=self.user, author=self.user1) 
        un_follow.delete() 
        self.assertEqual(following.count(), 0) 
 
    def test_follow_post(self): 
 
        follow = Follow.objects.create(user=self.user, author=self.user1) 
        following = Follow.objects.filter(user=self.user) 
        self.client_auth2.post( 
        reverse("new_post"), 
        data={ 
            "text": "test test", 
            "group": self.group.id 
        }, 
        follow=True 
        ) 
        response = self.client_auth.get(reverse("follow_index")) 
        self.assertContains(response, "test test") 
        response = self.client_auth2.get(reverse("follow_index")) 
        self.assertNotContains(response, "test test") 
     
    def test_comments(self): 
        post = Post.objects.create(text="test text", 
                                   author=self.user1) 
        edit_group = Group.objects.create(title="edit_group", 
                                          slug="edit_group") 
 
        response = self.client.post( 
            reverse("add_comment",  
            kwargs={"username": post.author.username, 
            "post_id": post.id}), 
            {"text": "тест тест",} 
        ) 
        login = reverse("login") 
        comment = reverse("add_comment", kwargs= 
                    {"username": post.author.username, 
                     "post_id": post.id}) 
        self.assertEqual(response.status_code, 302)   
        self.assertRedirects(response, f"{login}?next={comment}")
        