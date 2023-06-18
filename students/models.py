from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save
from django.utils.html import escape, mark_safe
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):
    is_student = models.BooleanField(default=False, verbose_name="студент")
    is_teacher = models.BooleanField(default=False, verbose_name="преподаватель")


class Tag(models.Model):
    name = models.CharField(max_length=30, verbose_name="название")
    color = models.CharField(max_length=7, default='#007bff', verbose_name="цвет")

    def __str__(self):
        return self.name

    def get_html_badge(self):
        name = escape(self.name)
        color = escape(self.color)
        html = '<span class="badge badge-primary" style="background-color: %s">%s</span>' % (color, name)
        return mark_safe(html)


class Quiz(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quizzes', verbose_name="создатель")
    name = models.CharField(max_length=255, verbose_name="название")
    tags = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='quizzes')

    class Meta:
        verbose_name = "Тест"
        verbose_name_plural = "Тесты"

    def __str__(self):
        return self.name


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions', verbose_name="тест")
    text = models.CharField(max_length=255, verbose_name="вопрос")

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"

    def __str__(self):
        return self.text


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers', verbose_name="вопрос")
    text = models.CharField(max_length=255, verbose_name="ответ")
    is_correct = models.BooleanField('Correct answer', default=False)

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"

    def __str__(self):
        return self.text


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="пользователь")
    award_points = models.PositiveIntegerField(default=0, verbose_name="очки профиль")
    location = models.CharField(max_length=30, blank=True, verbose_name="адрес")
    birthdate = models.DateField(null=True, blank=True, verbose_name="день рождения")

    def get_award_points(self, point):
        self.award_points += point
        self.save()

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, verbose_name="пользователь")
    quizzes = models.ManyToManyField(Quiz, through='TakenQuiz', verbose_name="пройденные тесты")
    interests = models.ManyToManyField(Tag, related_name='interested_students', verbose_name="интересы")

    def get_unanswered_questions(self, quiz):
        answered_questions = self.quiz_answers \
            .filter(answer__question__quiz=quiz) \
            .values_list('answer__question__pk', flat=True)
        questions = quiz.questions.exclude(pk__in=answered_questions).order_by('text')
        return questions

    class Meta:
        verbose_name = "Студент"
        verbose_name_plural = "Студенты"

    def __str__(self):
        return '{} - {}'.format(self.user.username, self.user.email)


class TakenQuiz(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='taken_quizzes', verbose_name="студент")
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='taken_quizzes', verbose_name="тест")
    score = models.FloatField(verbose_name="оценка")
    date = models.DateTimeField(auto_now_add=True, verbose_name="дата")

    class Meta:
        verbose_name = "Пройденный тест"
        verbose_name_plural = "Пройденные тесты"

    def __str__(self):
        return '{}. {} {}%'.format(self.quiz, self.student, self.score)


class StudentAnswer(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='quiz_answers', verbose_name="студент")
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='+', verbose_name="ответ")

    class Meta:
        verbose_name = "Ответ студента"
        verbose_name_plural = "Ответы студента"

    def __str__(self):
        return '{} {}'.format(self.student, self.answer)

