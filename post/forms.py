from ckeditor.fields import RichTextField
from django import forms
from .models import Post


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
        fields = ['body', 'post_picture', 'title']  # Add or remove fields as needed
