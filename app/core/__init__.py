#
# # class PostLikeView(MustBeLogingCustomView):
# #     http_method_names = ['get']
# #
# #     def setup(self, request, *args, **kwargs):
# #         """Initialize the next_page_explorer_post_id, user, self.post."""
# #         self.next_page_explorer_post_id = reverse_lazy('explorer', kwargs={'pk': kwargs['post_id']})  # noqa
# #         self.user = request.user.profile  # noqa
# #         self.post = get_object_or_404(Post, pk=kwargs['post_id'])  # noqa
# #         return super().setup(request, *args, **kwargs)
# #
# #     def get(self, request, *args, **kwargs):
# #         post = get_object_or_404(Post, pk=kwargs['post_id'])
# #
# #         # Annotate the queryset with like and dislike counts
# #         post_with_counts = Post.objects.filter(pk=post.id).annotate(
# #             num_likes=Count('likes'),
# #             num_dislikes=Count('dislikes')
# #         ).first()
# #
# #         response_data = {'success': False}
# #
# #         if not post.likes == self.user:
# #             post.likes = self.user
# #             post.save()
# #             response_data['success'] = True
# #             response_data['likes'] = post_with_counts.num_likes
# #             response_data['dislikes'] = post_with_counts.num_dislikes
# #             response_data['message'] = "You have liked this post"
# #             if post.dislikes == self.user:
# #                 post.dislikes = None
# #                 post.save()
# #                 response_data['remove_dislike'] = True
# #                 response_data['remove_dislike_message'] = "You have removed your dislike from this post"
# #         elif not post.dislikes == self.user:
# #             post.dislikes = self.user
# #             post.save()
# #             response_data['success'] = True
# #             response_data['dislikes'] = post_with_counts.num_dislikes
# #             response_data['likes'] = post_with_counts.num_likes
# #             response_data['message'] = "You have disliked this post"
# #             if post.likes == self.user:
# #                 post.likes = None
# #                 post.save()
# #                 response_data['remove_like'] = True
# #                 response_data['remove_like_message'] = "You have removed your like from this post"
# #
# #         return JsonResponse(response_data)
# #
# #
# #
# #
# #
# #
#
#
#
# #         url account
# path("profilesall/<int:pk>/", ShowAllProfilesView.as_view(), name="profile_detail_all"),
# #
# #
# #
# #
# #
# #
# #
# #
# #  views.py account
#
#
#
# class ShowAllProfilesView(ListView):
#     """
#     Displays profiles of all users.
#     """
#
#     model = Profile
#     context_object_name = 'profiles'
#     template_name = 'accounts/profile_detail.html'
#     http_method_names = ['get']
#
#     def get_queryset(self):
#         """
#         Returns the queryset of all profiles.
#         """
#         return Profile.objects.all()
#
#     def get_context_data(self, **kwargs):
#         """
#         Adds counts of followers and following to the context for each profile.
#         """
#         context = super().get_context_data(**kwargs)
#
#         # Iterate through profiles and add counts of followers and following for each profile
#         for profile in context['profiles']:
#             profile_counts = Profile.objects.filter(user=profile.user).aggregate(
#                 num_followers=Count('followers'),
#                 num_following=Count('following')
#             )
#             profile.followers_count = profile_counts['num_followers']
#             profile.following_count = profile_counts['num_following']
#
#         return context
#
#
#
#
#
