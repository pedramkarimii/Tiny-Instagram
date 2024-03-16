from ckeditor.fields import RichTextField
from django import forms

from .models import Post, Comment


class UpdatePostForm(forms.ModelForm):
    """
    Form for updating a post.
    """
    body = RichTextField(config_name='default', )
    post_picture = forms.ImageField(label='Profile Picture', required=False,
                                    widget=forms.FileInput(attrs={'class': 'form-control'}))
    title = forms.SlugField()

    class Meta:
        model = Post
        fields = ['body', 'post_picture', 'title']

    def clean_body(self):
        body = self.cleaned_data.get('body')
        if len(body) < 1:
            raise forms.ValidationError('Body must be at least 1 character long.')
        elif len(body) > 500:
            raise forms.ValidationError('Body must be less than 500 characters long.')
        return body


class CreatCommentForm(forms.ModelForm):
    """
    Form for creating a comment.
    """
    # body = RichTextField(config_name='default', )

    class Meta:
        model = Comment
        fields = ('comments',)

    def clean_body(self):
        body = self.cleaned_data.get('body')
        if len(body) < 1:
            raise forms.ValidationError('Body must be at least 1 character long.')
        elif len(body) > 500:
            raise forms.ValidationError('Body must be less than 500 characters long.')
        return body
