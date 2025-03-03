from django import forms
from django.core.exceptions import ValidationError

from notes.models import Note

TAG_CHOICES = [
    ('', 'No tag'),
    ('personal', 'Personal'),
    ('work', 'Work'),
    ('important', 'Important'),
    ('list', 'List'),
]


class NoteForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Title'}))
    content = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Content', 'id': 'hs-autoheight-textarea'}))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(NoteForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Note
        fields = ('title', 'content',)

    def save(self, commit=True):
        instance = super(NoteForm, self).save(commit=False)

        instance.user = self.user
        instance.title = self.cleaned_data['title']
        instance.content = self.cleaned_data['content']
        if commit:
            instance.save()
            return instance


class NoteEditForm(forms.ModelForm):
    title = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Title', 'maxlength': 100}))
    content = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Content', 'id': 'hs-autoheight-textarea'}))
    pinned = forms.BooleanField(required=False, initial=False, widget=forms.CheckboxInput)
    private = forms.BooleanField(required=False, initial=False, widget=forms.CheckboxInput)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = Note
        fields = ('title', 'content', 'pinned',)

    def save(self, commit=True):
        # Make sure we are updating the existing instance, not creating a new one
        instance = super().save(commit=False)
        instance.user = self.user

        # Encrypt the title and content before saving
        instance.title = self.cleaned_data['title']
        instance.pinned = self.cleaned_data['pinned']
        instance.content = self.cleaned_data['content']

        if commit:
            instance.save()
            return instance


class NotePasswordForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}))

    class Meta:
        model = Note
        fields = ('password1', 'password2',)


class NotePasswordCheckForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Note password'}))

    class Meta:
        model = Note
        fields = ('password',)
