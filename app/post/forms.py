from ckeditor.widgets import CKEditorWidget
from django import forms
from django.forms.widgets import TextInput
from .models import Post, Comment, Image
from django.forms import ClearableFileInput


class SearchForm(forms.Form):
    """
    Form for searching.
    """
    search = forms.CharField(label='Search', max_length=100)


class ImageForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['images'].widget.attrs['multiple'] = True

    class Meta:
        model = Image
        fields = ['images']
        widgets = {'images': ClearableFileInput()}


class UpdatePostForm(forms.ModelForm):
    """
    Form for updating a post.
    """
    title = forms.CharField(label='Title', required=True, widget=TextInput(attrs={
        'class': 'mt-1 mb-8 pt-2 py-2 px-4 focus:ring-indigo-500 focus:border-indigo-500 block w-full'
                 ' shadow-sm sm:text-sm border-gray-300 rounded-md'}))
    body = forms.CharField(label='Body',
                           required=True, widget=CKEditorWidget(attrs={'class': 'mt-1 mb-4 pt-2 py-2 px-4 '
                                                                                'focus:ring-indigo-500 '
                                                                                'focus:border-indigo-500 block w-full '
                                                                                'shadow-sm sm:text-sm border-gray-300 '
                                                                                'rounded-md'}))
    Image = forms.ImageField(label='Post Image', required=True)

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

    def __init__(self, *args, **kwargs):
        post_id = kwargs.pop('post_id', None)
        super().__init__(*args, **kwargs)
        if post_id:
            self.fields['reply'].queryset = Comment.objects.filter(post_id=post_id, is_reply=True)

    comments = forms.CharField(
        label='comments', required=False,
        widget=CKEditorWidget(attrs={'class': 'mt-1 mb-4 pt-2 py-2 px-4 focus:ring-indigo-500 '
                                              'focus:border-indigo-500 block w-full '
                                              'shadow-sm sm:text-sm border-gray-300 '
                                              'rounded-md'}))
    reply = forms.ModelChoiceField(queryset=Comment.objects.all(), required=False, widget=forms.Select(attrs={
        'class': 'mt-1 mb-4 pt-2 py-2 px-4 focus:ring-indigo-500 focus:border-indigo-500 block w-s'
                 ' shadow-sm sm:text-sm border-gray-300 rounded-md'}))
    is_reply = forms.BooleanField(label='Is Reply', required=False, widget=forms.CheckboxInput(attrs={
        'class': 'mt-1 mb-4 pt-2 px-4 text-indigo-600 border-gray-300 rounded-md'}))

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
