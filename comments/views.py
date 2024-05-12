from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from comments.serializers import CommentSerializer
from comments.models import Comment
from recipes.models import Recipe


class CommentListView(generics.ListCreateAPIView[Comment]):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        recipe_id = self.kwargs.get("recipe_id")
        if not recipe_id:
            return Comment.objects.all()
        return Comment.objects.filter(recipe_id=recipe_id)

    def list(self, request, *args, **kwargs):
        if not self.kwargs.get("recipe_id"):
            return Response(data={"message": "Recipe id does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        response = super().list(request, *args, **kwargs)
        response.data = {"message": "Successfully Read Comments", "comment_list": response.data}
        response.status_code = status.HTTP_200_OK
        return response

    def perform_create(self, serializer):
        user = self.request.user
        recipe_id = self.kwargs.get("recipe_id")

        try:
            recipe = Recipe.objects.get(id=recipe_id)
        except Recipe.DoesNotExist:
            raise NotFound(detail="Recipe is Not Found")

        serializer.save(user=user, recipe=recipe)
