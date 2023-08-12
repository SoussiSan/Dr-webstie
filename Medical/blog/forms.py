from django import forms
from .models import Post


class CreatePost(forms.ModelForm):
    message = forms.CharField(max_length=400)
    picture = forms.ImageField(required=False)
    title = forms.CharField(max_length=50)

    class Meta:
        model = Post
        fields = ['message', 'picture', 'title']

