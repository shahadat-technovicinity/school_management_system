from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import TeacherViewSet, TeacherListView


# Create a router and register our viewset
router = DefaultRouter()
router.register(r"", TeacherViewSet, basename="teacher")

# The API URLs are determined automatically by the router
# Available endpoints:
# - POST   /teachers/           -> Create a new teacher
# - GET    /teachers/           -> List all teachers (paginated)
# - GET    /teachers/{id}/      -> Retrieve a specific teacher
# - PUT    /teachers/{id}/      -> Update a teacher (full)
# - PATCH  /teachers/{id}/      -> Update a teacher (partial)
# - DELETE /teachers/{id}/      -> Delete a teacher
# - GET    /teachers/statistics/ -> Get teacher statistics

urlpatterns = [
    path("list/", TeacherListView.as_view(), name="teacher-list"),

    path("", include(router.urls)),
]





