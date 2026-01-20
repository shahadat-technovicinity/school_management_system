from django.contrib.auth.base_user import BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, username, name, phone_number, role, password, **extra_fields):
        if not username:
            raise ValueError('The Username field is required')
        if not name:
            raise ValueError('The Name field is required')
        if not role:
            raise ValueError('The Role field is required')
        if not phone_number:
            raise ValueError('The Role field is required')

        user = self.model(username=username, name=name, phone_number=phone_number, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, name, phone_number, role="ADMIN", password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, name, phone_number, role, password, **extra_fields)
