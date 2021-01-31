from django.db import models
from users.models import User


class Group(models.Model):
    def __str__(self):
        return f"Сообщество {self.title}"
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(default="У этого сообщества нет описания", blank=True)


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField("date published", auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, blank=True, null=True)
