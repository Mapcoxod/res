from ckeditor.fields import RichTextField
from django.db import models
from django.db.models import Avg
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from courses.fields import OrderField
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils import timezone
from autoslug import AutoSlugField

import numpy as np

class Subject(models.Model):
    title = models.CharField(max_length=200, verbose_name="название")
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ('title',)
        verbose_name = "Предмет"
        verbose_name_plural = "Предметы"

    def __str__(self):
        return self.title


class Course(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='courses_created',
        on_delete=models.CASCADE,
        verbose_name="Преподаватель"
    )
    subject = models.ForeignKey(Subject, verbose_name="предмет", related_name='courses', on_delete=models.CASCADE)
    title = models.CharField(max_length=200, verbose_name="название")
    slug = AutoSlugField(populate_from='title', unique_with='created__month')
    overview = models.TextField(verbose_name="описание")
    created = models.DateTimeField(auto_now_add=True, verbose_name="дата создания")
    students = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='courses_joined', blank=True, verbose_name="студенты")

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"
        ordering = ('-created',)

    # def save(self, *args, **kwargs):
        # if not self.slug:
            # self.slug = slugify(self.title)
        # super(Course, self).save(*args, **kwargs)

    def average_rating(self):
        # all_ratings = map(lambda x: x.rating, self.reviews.all())
        # return np.mean(all_ratings)
        return self.reviews.aggregate(Avg('rating'))['rating__avg']

    def __str__(self):
        return self.title


class Module(models.Model):
    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE, verbose_name="курс")
    title = models.CharField(max_length=200, verbose_name="название")
    description = models.TextField(blank=True, verbose_name="описание")
    content = RichTextField(verbose_name="содержание", null=True, blank=True)
    order = OrderField(blank=True, for_fields=['course'])

    class Meta:
        ordering = ['order']
        verbose_name = "Модуль"
        verbose_name_plural = "Модули"

    def __str__(self):
        return '{}. {}'.format(self.order, self.title)


class ItemBase(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_related', on_delete=models.CASCADE, verbose_name="преподаватель")
    title = models.CharField(max_length=250, verbose_name="название")
    created = models.DateTimeField(auto_now_add=True, verbose_name="дата создания")
    updated = models.DateTimeField(auto_now=True, verbose_name="дата обновления")

    class Meta:
        abstract = True

    def render(self):
        return render_to_string('courses/content/{}.html'.format(self._meta.model_name), {'item': self})

    def __str__(self):
        return self.title

class Text(ItemBase):
    content = models.TextField(verbose_name="содержание")

class File(ItemBase):
    file = models.FileField(upload_to='files', verbose_name="файл")

class Image(ItemBase):
    file = models.FileField(upload_to='images', verbose_name="фото")

class Video(ItemBase):
    url = models.URLField(verbose_name="видео")


class Content(models.Model):
    module = models.ForeignKey(Module, related_name='contents', on_delete=models.CASCADE, verbose_name="модуль")
    content_type = models.ForeignKey(ContentType, limit_choices_to={'model__in':('text', 'video', 'image', 'file')}, on_delete=models.CASCADE, verbose_name="тип контента")
    object_id = models.PositiveIntegerField(verbose_name="айди объекта")
    item = GenericForeignKey('content_type', 'object_id')
    order = OrderField(blank=True, for_fields=['module'])

    class Meta:
        ordering = ['order']
        verbose_name = "Контент"
        verbose_name_plural = "Контент"


class Review(models.Model):
    RATING_CHOICES = (
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5')
    )
    course = models.ForeignKey(Course, related_name='reviews', on_delete=models.CASCADE, verbose_name="курс")
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name="дата публикации")
    user_name = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='reviewers', on_delete=models.CASCADE, verbose_name="имя пользователя")
    comment = models.CharField(max_length=200, verbose_name="комментарий")
    rating = models.IntegerField(choices=RATING_CHOICES, verbose_name="оценка")


# https://github.com/pinax/pinax-badges
class BadgeAward(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="badges_earned", on_delete=models.CASCADE, verbose_name="пользователь")
    awarded_at = models.DateTimeField(default=timezone.now, verbose_name="награждено")
    slug = models.CharField(max_length=255)
    level = models.IntegerField(verbose_name="уровень")

    def __str__(self):
        return "{} : {} points - level {}".format(self.user.username, self.user.profile.award_points, self.level)
