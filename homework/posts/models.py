from django.db import models

from users.models import User


class Group(models.Model):

    def __str__(self):
        return f"Сообщество {self.title}"
    title = models.CharField(
        verbose_name='Заголовок',
        max_length=200,
        help_text='Придумайте заголовок для группы',
    )
    slug = models.SlugField(
        verbose_name='Уникальный идентификатор',
        unique=True,
        help_text='Простое, как можно более короткое слово',
    )
    description = models.TextField(default='У этого сообщества нет описания', blank=True)


class Post(models.Model):
    def __str__(self):
        return self.text[:15]

    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Текст поста должен быть крутым',
    )
    pub_date = models.DateTimeField(verbose_name='Дата публикации', auto_now_add=True, db_index=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор', related_name='user_posts')
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Группа')
    image = models.ImageField(upload_to='posts/', blank=True, null=True)


class Comment(models.Model):
    def __str__(self):
        return self.text[:15]

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name='Родительский пост')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name='Автор')
    text = models.TextField(verbose_name='Текст комментария', help_text='Ведите себя прилично в комментариях')
    created = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True)


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower', verbose_name='Подписчик')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following', verbose_name='Автор')
