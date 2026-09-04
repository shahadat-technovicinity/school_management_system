from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TeacherAndStaffViewSet, EmployeeUserDropdownView

# Create a router and register our viewset
router = DefaultRouter()
router.register(r"", TeacherAndStaffViewSet, basename="teacher-staff")

# The API URLs are determined automatically by the router
# Available endpoints:
# - POST   /teachers-staff/            -> Create a new teacher/staff profile
# - GET    /teachers-staff/            -> List all teachers/staff (paginated)
# - GET    /teachers-staff/{id}/       -> Retrieve a specific teacher/staff
# - PUT    /teachers-staff/{id}/       -> Update a profile (full)
# - PATCH  /teachers-staff/{id}/       -> Update a profile (partial)
# - DELETE /teachers-staff/{id}/       -> Delete a profile
# - GET    /teachers-staff/statistics/ -> Get teacher/staff statistics
# - GET    /teachers-staff/users-dropdown/ -> List users available for profile creation

urlpatterns = [
    path("users-dropdown/", EmployeeUserDropdownView.as_view(), name="employee-users-dropdown"),
    path("", include(router.urls)),
]