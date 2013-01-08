from django.db import models
import basic_models

import datetime



class Category(basic_models.SlugModel):
    pass

class Post(basic_models.SlugModel):
    category = models.ForeignKey(Category, null=True, blank=True)
    body     = models.TextField()

    def create_comment(self, **kwargs):
        return Comment.objects.create(post=self, **kwargs)

class Comment(basic_models.DefaultModel):
    post = models.ForeignKey(Post)
    body = models.TextField()
