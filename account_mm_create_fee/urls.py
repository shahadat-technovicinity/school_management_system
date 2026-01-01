from django.urls import path
from .views import *


urlpatterns = [
    path("create_free/", FeeListCreateView.as_view(), name="create_free"),
    path("FeeCreateUpdateDelete/<int:pk>/", FeeCreateUpdateDelete.as_view(), name="create_free"),
    path("FormFilupListCreateView/", FormFilupListCreateView.as_view(), name="create_free"),
    path("FormFilupUpdateDelete/<int:pk>/", FormFilupUpdateDelete.as_view(), name="create_free"),

]

