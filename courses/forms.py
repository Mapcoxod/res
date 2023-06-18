from ckeditor.widgets import CKEditorWidget
from django import forms
from django.forms.models import inlineformset_factory
from courses.models import Course, Module, Review, Subject, Content
from django.forms.utils import pretty_name
from students.models import (
    User, Profile
)

class ModuleForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control', 'cols': 40, 'rows': 8}))
    content = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = Module
        exclude = ()
        fields = '__all__'


ModuleFormSet = inlineformset_factory(Course, Module, form=ModuleForm, fields=['title', 'description',], extra=2, can_delete=True)


class UserEditForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'readonly': True}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name',]

    # def clean(self):
    #     email = self.cleaned_data.get('email')
    #     if User.objects.filter(email=email).exists():
    #         raise forms.ValidationError("Email already exist")
    #     return self.cleaned_data


class ProfileEditForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ['location', 'birthdate']


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'cols': 40, 'rows': 15, 'class':'no-resize appearance-none block w-full bg-gray-200 text-gray-700 border border-gray-200 rounded py-3 px-4 mb-3 leading-tight focus:outline-none focus:bg-white focus:border-gray-500 h-48 resize-none'})
        }


class CourseCreateForm(forms.ModelForm):
    subject = forms.ModelChoiceField(queryset=Subject.objects.all(),widget=forms.Select(attrs={'class':'form-control'}), label="Предмет")
    title = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), label="Название")
    overview = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control', 'cols': 40, 'rows': 15}), label="Описание")

    class Meta:
        model = Course
        fields = ['subject', 'title', 'overview',]
