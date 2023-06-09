from django.urls import path
from views import *

urlpatterns = [
    path('/api/sign-up/', SignUpView.as_view(), name='signup'),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('/api/login', LoginView.as_view(), name='login-account'),
    path('api/announcements/<int:pk>/', AdvertisementUpdateView.as_view()),
    path('api/announcements/<int:pk>/accept/', AdvertisementAccept.as_view()),
    path('api/announcements/', AdvertisementListView.as_view()),
    path('api/admin/advertisements/<int:pk>/', AdvertisementDeleteView.as_view()),
    path('api/announcements/search/', AdvertisementSearchView.as_view()),
    path('api/announcements/<int:pk>/views/', AdvertisementViewsView.as_view()),
    path('api/users/<int:pk>/profile/', UserProfileView.as_view()),

]
