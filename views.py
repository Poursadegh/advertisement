import asyncio

from rest_framework.views import APIView
from django.contrib.auth import authenticate
from django.http import Http404
from django.shortcuts import render
from django.core.cache import cache
from django.views.generic import DetailView
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from models import Advertisement
from serializers import *
from rest_framework_simplejwt.tokens import RefreshToken, TokenObtainPairView, TokenRefreshView
from models import *
from serializers import *
from settings import CACHE_TTL
from rest_framework.pagination import PageNumberPagination


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class CustomTokenRefreshView(TokenRefreshView):
    pass


class SignUpView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response({'access': str(refresh.access_token), 'message': 'User created successfully'},
                        status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if user is None:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)

        return Response({'access': str(refresh.access_token)}, status=status.HTTP_200_OK)


class UserProfileView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdvertisementAccept(generics.UpdateAPIView):
    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer
    permission_classes = [permissions.IsAdminUser]


class AdvertisementUpdateView(generics.UpdateAPIView):
    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer


class AdvertisementDeleteView(generics.DestroyAPIView):
    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
        except Http404:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdvertisementDeleteView(generics.DestroyAPIView):
    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer
    permission_classes = [permissions.IsAdminUser]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


async def get(request):
    advertisements = cache.get('advertisements')
    if not advertisements:
        queryset = Advertisement.objects.all()
        cache.set('advertisements', advertisements, CACHE_TTL)
        return render(request, 'advertisements/list.html', {'advertisements': advertisements})
    serializer = AdvertisementSerializer(queryset, many=True)
    await asyncio.sleep(2)
    return Response(serializer.data)


class AdvertisementPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


class AdvertisementListView(generics.ListAPIView):
    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = AdvertisementPagination


class AdvertisementSearchView(generics.ListAPIView):
    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer

    def get_queryset(self):
        query = self.request.query_params.get('q')
        if query:
            queryset = Advertisement.objects.filter(title__icontains=query)
        else:
            queryset = self.queryset
        return queryset


class AdvertisementViewsView(generics.RetrieveAPIView):
    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        views = instance.views
        return Response({"views": views}, status=status.HTTP_200_OK)


class UserProfileView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdvertisementDetailView(DetailView):
    model = Advertisement

    def get(self, request, *args, **kwargs):
        advertisement = self.get_object()
        AdvertisementUpdateView.delay()  # trigger the Celery task
        return super().get(request, *args, **kwargs)
