from django.contrib.postgres.search import TrigramSimilarity
from django.shortcuts import render
from django.db.models.functions import Greatest
from posts.models import Post
from .forms import SearchForm


def search(request):
    post = Post.objects.all()
    form = SearchForm()
    if request.method == 'GET':
        form = SearchForm(request.GET)
        if form.is_valid():
            cd = form.cleaned_data['search']
            posts = post.annotate(
                similarity=Greatest(TrigramSimilarity('name', cd),
                                    TrigramSimilarity('surname', cd),
                                    TrigramSimilarity('patronymic', cd)
                                    ).filter(similarity__gt=0.1).order_by('-similarity'))
            return render(request, 'search.html', {'posts': posts, 'form': form, })
