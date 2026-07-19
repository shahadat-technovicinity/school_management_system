from django.db import models
from django.conf import settings
from .models import RolePermission


def check_user_feature_permission(user, app_name, feature_slug, action='view'):
    """
    ব্যবহার: check_user_feature_permission(request.user, 'admissions', 'student_admission', 'create')
    """
    if not user.is_authenticated or not user.role:
        return False
        
    # সুপারঅ্যাডমিন হলে বাইপাস লজিক চাইলে এখানে দিতে পারেন
    if user.role.name == 'Admin':
        return True

    # অ্যাকশন ফিল্ড ডাইনামিকালি চেক (can_view, can_create ইত্যাদি)
    filter_kwargs = {
        'role': user.role,
        'app_name': app_name,
        'feature_slug': feature_slug,
        f'can_{action}': True
    }
    
    return RolePermission.objects.filter(**filter_kwargs).exists()