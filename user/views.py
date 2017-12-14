from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status

from django.contrib.auth import authenticate
from django.contrib.auth.views import logout

from .models import User
from .api.serializers import UserSerializer
from games.api.serializers import GameSerializer


class UserRegister(APIView):
    permission_classes = (AllowAny,)
    
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'This username is already taken'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogin(APIView):
    permission_classes = (AllowAny,)
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user:
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)


class UserLogout(APIView):
    def post(self, request):
        logout(request)
        return Response({}, status=status.HTTP_200_OK)
        

class UserMe(APIView):
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request):
        user = User.objects.get(username=request.data.get('username'))
        serializer = UserSerializer(user, request.data)
        return self.get(user)


class UserMeGames(APIView):
    def get(self, request):
        games = [player.game for player in request.user.player_set.iterator()]
        serializer = GameSerializer(games, many=True, context={'no_board': True})
        
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserMeFinishedGames(APIView):
    def get(self, request):
        games = [player.game for player in request.user.player_set.iterator() if player.game.finished]
        serializer = GameSerializer(games, many=True, context={'no_board': True})
        
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserInfo(APIView):
    def get(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

