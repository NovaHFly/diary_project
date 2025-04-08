from rest_framework.permissions import IsAuthenticated


class IsAuthor(IsAuthenticated):
    def has_object_permission(self, request, view, obj) -> bool:
        return obj.author == request.user


class IsStaff(IsAuthenticated):
    def has_permission(self, request, view) -> bool:
        return super().has_permission(request, view) and request.user.is_staff

    def has_object_permission(self, request, view, obj) -> bool:
        return self.has_permission(request, view)
