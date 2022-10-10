from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.forms import NewUserForm
from accounts.serializers import UserSerializer
from bookstore import settings
from rest_framework.authtoken.models import Token


def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if request.GET.get('next'):
                return HttpResponseRedirect(request.GET.get('next'))
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
        else:
            context = {
                'username': username,
                'errorMessage': 'کاربر مورد نظر یافت نشد'
            }
            return render(request, 'accounts/login.html', context)
    else:
        return render(request, 'accounts/login.html', {})


def register_view(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
    form = NewUserForm()
    return render(request, 'accounts/register.html', context={"register_form": form})


@staff_member_required
@api_view(['GET', 'POST'])
def users_list_api(request, format=None):
    if request.method == 'GET':
        users = User.objects.values()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    # if request.method == 'POST':
    #   serializer = DrinkSerializer(data=request.data)
    #  if serializer.is_valid():
    #     serializer.save()
    #    return Response(serializer.data, status=status.HTTP_201_CREATED)


def logout_view(request):
    logout(request)
    return HttpResponse('logout shodid')


@api_view(['GET', 'POST'])
def login_api(request):
    #user_name = request.data['username']
    #password = request.data['password']
    username = request.data.get('username')
    password = request.data.get('password')
    device = request.data.get('device')

    user = authenticate(username=username, password=password)
    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response(data={'token': token.key}, status=status.HTTP_200_OK)
    else:
        return Response(data='username or password invalid', status=status.HTTP_401_UNAUTHORIZED)


