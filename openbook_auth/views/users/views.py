from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from openbook_auth.views.authenticated_user.serializers import GetAuthenticatedUserSerializer
from openbook_auth.views.users.serializers import SearchUsersSerializer, SearchUsersUserSerializer, GetUserSerializer, \
    GetUserUserSerializer, GetBlockedUserSerializer
from openbook_moderation.permissions import IsNotSuspended
from openbook_common.responses import ApiMessageResponse
from django.utils.translation import ugettext_lazy as _


class SearchUsers(APIView):
    permission_classes = (IsAuthenticated, IsNotSuspended)

    def get(self, request):
        query_params = request.query_params.dict()
        serializer = SearchUsersSerializer(data=query_params)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        count = data.get('count', 20)
        query = data.get('query')

        user = request.user

        users = user.search_users_with_query(query=query)

        users_serializer = SearchUsersUserSerializer(users[:count], many=True, context={'request': request})

        return Response(users_serializer.data, status=status.HTTP_200_OK)


class GetUser(APIView):
    permission_classes = (IsAuthenticated, IsNotSuspended)

    def get(self, request, user_username):
        request_data = request.data.copy()
        request_data['username'] = user_username

        serializer = GetUserSerializer(data=request_data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        username = data.get('username')

        user = request.user

        if user.username == username:
            user_serializer = GetAuthenticatedUserSerializer(user, context={"request": request})
        else:
            retrieved_user = user.get_user_with_username(username=username)
            user_serializer = GetUserUserSerializer(retrieved_user, context={"request": request})

        return Response(user_serializer.data, status=status.HTTP_200_OK)


class BlockUser(APIView):
    permission_classes = (IsAuthenticated, IsNotSuspended)

    def post(self, request, user_username):
        request_data = request.data.copy()
        request_data['username'] = user_username

        serializer = GetUserSerializer(data=request_data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        username = data.get('username')

        user = request.user

        with transaction.atomic():
            blocked_user = user.block_user_with_username(username)

        user_serializer = GetBlockedUserSerializer(blocked_user, context={"request": request})

        return Response(user_serializer.data, status=status.HTTP_200_OK)


class UnblockUser(APIView):
    permission_classes = (IsAuthenticated, IsNotSuspended)

    def post(self, request, user_username):
        request_data = request.data.copy()
        request_data['username'] = user_username

        serializer = GetUserSerializer(data=request_data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        username = data.get('username')

        user = request.user

        with transaction.atomic():
            unblocked_user = user.unblock_user_with_username(username)

        user_serializer = GetBlockedUserSerializer(unblocked_user, context={"request": request})

        return Response(user_serializer.data, status=status.HTTP_200_OK)
