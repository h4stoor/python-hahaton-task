from rest_framework import serializers

from ..models import Player, Game, Move


class PlayerSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source='user.id')
    game = serializers.IntegerField(source='game_id')
    name = serializers.CharField(source='user.username')
        
    class Meta:
        model = Player
        fields = ('won', 'owner', 'name', 'first', 'user', 'game')
    

class GameSerializer(serializers.ModelSerializer):
    players = PlayerSerializer(many=True, source='player_set')
    board = serializers.JSONField()
    
    def to_representation(self, obj):
        data = super().to_representation(obj)

        if self.context.get('no_board'):
            data.pop('board')
        
        return data
    
    class Meta:
        model = Game
        fields = ('id', 'players_count', 'board', 'players', 'started', 'finished', 'surrendered', 'draw')


class MoveSerializer(serializers.ModelSerializer):
    player = serializers.IntegerField(source='player.id')
    
    def create(self, data):
        player = Player.objects.get(pk=self.context.get('player'))
        game = Game.objects.get(pk=self.context.get('game'))
        x = data.get('x')
        y = data.get('y')
        
        move = Move.objects.create(player=player, game=game, x=x, y=y)
        
        return move
    
    class Meta:
        model = Move
        fields = ('id', 'player', 'timestamp', 'x', 'y')
