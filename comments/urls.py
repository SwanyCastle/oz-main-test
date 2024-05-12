from django.urls import path

from comments import views

urlpatterns = [path("<int:recipe_id>", views.CommentListView.as_view(), name="comment-list")]
