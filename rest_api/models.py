from django.db import models
# from django.utils import timezone
from rest_api.managers import TagManager

class User(models.Model):
    name = models.CharField(max_length=128, verbose_name='Никнейм')
    birthday = models.DateField(verbose_name='Дата рождения')
    registration_date = models.DateField(verbose_name='Дата регистрации')
    email = models.EmailField(verbose_name='Email')
    avatar = models.ForeignKey('Pictures', null=True, blank=True,
                               verbose_name='Аватарка', on_delete=models.SET_NULL)
    description = models.TextField(
        null=True, blank=True, verbose_name='Описание')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering=['name']

class Subscription(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Автор', related_name='author')
    subscriber = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Подписчик', related_name='subscriber')
    date = models.DateTimeField(
        verbose_name='Дата подписки', auto_now_add=True)

    def __str__(self):
        return (self.author + '-' + self.subscriber)

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

class Publication(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Автор')
    title = models.CharField(
        max_length=1024, verbose_name='Заголовок', null=True, blank=True)
    description = models.TextField(
        verbose_name='Описание', null=True, blank=True)
    date = models.DateTimeField(
        verbose_name='Дата создания', auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Публикация'
        verbose_name_plural = 'Публикации'


class Pictures(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Автор')
    publication = models.ForeignKey(
        Publication, on_delete=models.CASCADE, verbose_name='Публикация', null=True, blank=True)
    token = models.CharField(max_length=256, verbose_name='Токен картинки')

    # def __str__(self):
    #     return self.name

    class Meta:
        verbose_name = 'Картинка'
        verbose_name_plural = 'Картинки'


class Comment(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Автор')
    publication = models.ForeignKey(
        Publication, on_delete=models.CASCADE, verbose_name='Публиация')
    comment = models.TextField(verbose_name='Комментарий')
    date = models.DateTimeField(
        verbose_name='Время комментария', auto_now_add=True)

    def __str__(self):
        return self.comment

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'


class Like(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Автор')
    publication = models.ForeignKey(
        Publication, on_delete=models.CASCADE, verbose_name='Публиация', null=True, blank=True)
    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, verbose_name='Комментарий', null=True, blank=True)
    date = models.DateTimeField(
        verbose_name='Время комментария', auto_now_add=True)

    def __str__(self):
        if self.comment != None:
            return self.comment
        return self.publication

    class Meta:
        verbose_name = 'Лайк'
        verbose_name_plural = 'Лайки'


class Tag(models.Model):
    publication = models.ManyToManyField(
        Publication, verbose_name='Публиация', blank=True)
    title = models.CharField(
        max_length=128, verbose_name='Заголовок', null=True, blank=True)

    objects = TagManager()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'