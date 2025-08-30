# views.py
from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView
from .serializers import UserRegistrationSerializer
from rest_framework import status
from rest_framework.response import Response
from .models import User
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import make_password


#user list
class userlistview(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer    


#user registration class
class UserRegistrationView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer       

    def perform_create(self, serializer):
        """
        user save
        """
        serializer.save()



#user username and password update class
class UpdateUsernamepassView(UpdateAPIView):
    queryset = User.objects.all()  # all users/ all register user headmaster, admin, teacher, staff
    serializer_class = UserRegistrationSerializer
    lookup_field = 'pk'  # Primery key 

    #Change username
    def perform_update(self, serializer):
        if 'username' in self.request.data:
            serializer.save(username=self.request.data['username'])
        else:
            serializer.save()


    #Change Password
        if 'password' in self.request.data:
            # cheak old and new password
            user = self.get_object()
            old_password = self.request.data.get('old_password')
            new_password = self.request.data.get('password')
            if user.check_password(old_password):  # cheak old password
                user.password = make_password(new_password)  # new password
                user.save()
            else:
                return Response({"detail": "Old password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)
            

#user profile delete class
class UserProfileDeleteview(DestroyAPIView):
    queryset = User.objects.all()  #all user call
    serializer_class = UserRegistrationSerializer  #serializer class call serializer
    lookup_field = 'id'    


            


