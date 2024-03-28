from django import forms
from .models import Post, Comment, Image


class SearchForm(forms.Form):
    """
    Form for searching.
    """
    search = forms.CharField(label='Search', max_length=100)


class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['post_image', 'images']
        labels = {
            'post_image': 'Owner',
            'images': 'Image',
        }

    # def clean_images(self):
    #     images = self.cleaned_data.get('images')
    #     if image.size > 10485760:
    #         raise forms.ValidationError('Image size must be less than 10MB.')
    # def clean_post_image(self):
    #     post_image = self.cleaned_data.get('post_image')
    #     if post_image.user == self.request.user.profile:
    #         raise forms.ValidationError('You cannot upload an image to yourself.')
    #     return post_image
    #
    # def clean(self):
    #     cleaned_data = super().clean()
    #     images = cleaned_data.get('images')
    #     post_image = cleaned_data.get('owner_image')
    #
    #     if images and post_image:
    #         if images.user != post_image.owner.user:
    #             raise forms.ValidationError('You cannot upload an image to another user.')
    #     return cleaned_data


class UpdatePostForm(forms.ModelForm):
    """
    Form for updating a post.
    """

    # body = RichTextField(config_name='default',)
    Image = forms.ImageField(required=False,)

    class Meta:
        model = Post
        fields = ['body', 'title']

    def clean_body(self):
        body = self.cleaned_data.get('body')
        if len(body) < 1:
            raise forms.ValidationError('Body must be at least 1 character long.')
        elif len(body) > 500:
            raise forms.ValidationError('Body must be less than 500 characters long.')
        return body

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 1:
            raise forms.ValidationError('Title must be at least 1 character long.')
        elif len(title) > 50:
            raise forms.ValidationError('Title must be less than 50 characters long.')
        return title


class CreatCommentForm(forms.ModelForm):
    """
    Form for creating a comment.
    """

    # body = RichTextField(config_name='default', )

    class Meta:
        model = Comment
        fields = ('comments', 'reply', 'is_reply')

    def clean_body(self):
        body = self.cleaned_data.get('body')
        if len(body) < 1:
            raise forms.ValidationError('Body must be at least 1 character long.')
        elif len(body) > 500:
            raise forms.ValidationError('Body must be less than 500 characters long.')
        return body
