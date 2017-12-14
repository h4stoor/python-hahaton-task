from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from ..models import User


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(write_only=True)
    
    def create(self, data):
        user = User.objects.create_user(username=data['username'], password=data['password'])
        return user
    
    def update(self, user, data):
        user.username = data.get('username', user.username)
        user.save()
        return user
        
    class Meta:
        model = User
        fields = ('username', 'password', 'won', 'lost', 'won_by_surrender', 'draws', 'surrendered')
