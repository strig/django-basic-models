from django.db import models
import basic_models

import datetime



class Category(basic_models.SlugModel):
    pass

class Post(basic_models.SlugModel):
    category = models.ForeignKey(Category)
    body     = models.TextField()

class Comment(basic_models.DefaultModel):
    post = models.ForeignKey(Post)
    body = models.TextField()
