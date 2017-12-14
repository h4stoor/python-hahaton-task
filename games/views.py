from random import choice

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from . import const
from .models import Game, Player, Move
from .api.serializers import GameSerializer, PlayerSerializer, MoveSerializer


class GameRecent(APIView):
    def post(self, request):
        game = Game.objects.create()
        Player.objects.create(user=request.user, game=game, owner=True)
        
        serializer = GameSerializer(game)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def get(self, request):
        games = Game.objects.all().filter(finished=False)
        serializer = GameSerializer(games, many=True, context={'no_board': True})

        return Response(serializer.data, status=status.HTTP_200_OK)


class GameDetail(APIView):
    def get(self, request, pk):
        try:
            game = Game.objects.get(pk=pk)
        except Game.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
            
        serializer = GameSerializer(game)
        
        return Response(serializer.data, status=status.HTTP_200_OK)


class GameAction(APIView):    
    def _join(self, user, game, owner, guest):
        if game.players_count == 2:
            return const.ERROR_GAME_FULL, status.HTTP_400_BAD_REQUEST
        
        if user == owner.user:
            return const.ERROR_ALREADY_JOINED, status.HTTP_400_BAD_REQUEST
        
        Player.objects.create(user=user, game=game)
        
        game.players_count = 2
        game.save()
        
        serializer = GameSerializer(game)
        return serializer.data, status.HTTP_200_OK
    
    def _start(self, user, game, owner, guest):
            
        if user in [player.user for player in game.player_set.iterator()] and not game.started and game.players_count == 2:
            player = choice([owner, guest])
            player.first = True
            player.save()
            
            game.started = True
            game.now_turn = player.pk
            game.save()
            
            serializer = GameSerializer(game)
            return serializer.data, status.HTTP_200_OK
    
    def _leave(self, user, game, owner, guest):
        if user in [player.user for player in game.player_set.iterator()]:
            if game.started is False:
                player = user.player_set.get()
                
                if player == owner:
                    guest.owner = True
                    guest.save()
                
                player.delete()
                
                game.players_count = 1
                game.save()
                return {}, status.HTTP_200_OK
            else:
                return const.ERROR_GAME_ACTIVE, status.HTTP_400_BAD_REQUEST
        
        return const.ERROR_NOT_IN_GAME, status.HTTP_400_BAD_REQUEST
    
    def _surrender(self, user, game, owner, guest):
        if game.started and not game.finished:
            if user in [owner.user, guest.user]:
                winner, loser = ((owner, guest), (guest, owner))[user == owner.user]
                
                winner.user.won += 1
                winner.user.won_by_surrender += 1
                winner.user.save()

                loser.user.lost += 1
                loser.user.surrendered += 1
                loser.user.save()
                
                winner.won = True
                winner.save()
                
                game.finished = True
                game.surrendered = True
                game.save()
                
                return {}, status.HTTP_200_OK
            else:
                return {}, status.HTTP_400_BAD_REQUEST

    def post(self, request, pk, action):
        ACTIONS = {'join': self._join,
                   'start': self._start,
                   'leave': self._leave,
                   'surrender': self._surrender
                   }

        try:
            game = Game.objects.get(pk=pk)
        except Game.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        
        guest = False
        for player in game.player_set.iterator():
            if player.owner:
                owner = player
            else:
                guest = player
            
        if action in ACTIONS:
            _response, _status = ACTIONS[action](request.user, game, owner, guest)
            
            response = dict()
            if _status == status.HTTP_200_OK:
                response['success'] = True
                if _response:
                    response['game'] = _response
            else:
                response = _response
                    
            return Response(response, status=_status)
        
        return Response({}, status=status.HTTP_404_NOT_FOUND)
        

class GameMoves(APIView):
    def _get_second_player(self, game, player):
        players = list(game.player_set.iterator())
        players.remove(player)
        return players[0]
        
    def _make_move(self, x, y, game, player):
        other = self._get_second_player(game, player)
        if player.owner:
            SYMBOL = const.OWNER
        else:
            SYMBOL = const.GUEST
        
        game.board[x][y] = SYMBOL
        game.now_turn = other.pk
        game.save()
    
    def _check_winning_conditions(self, game, player):
        other = self._get_second_player(game, player)

        # win
        verticals = [[row[i] for row in game.board] for i in range(15)]
        diagonals1 = [[game.board[j][i+j] for j in range(15-i)] for i in range(11)] + \
                     [[game.board[i+j][j] for j in range(15-i)] for i in range(1, 11)]
        diagonals2 = [[game.board[i-j][j] for j in range(i+1)] for i in range(4, 15)] + \
                     [[game.board[14-j][i+j] for j in range(15-i)] for i in range(1, 11)]
                     
        for row in game.board + verticals + diagonals1 + diagonals2:
            for i in range(11):
                if row[i:i+5] in [list('o'*5), list('g'*5)]:
                    
                    player.user.won += 1
                    player.user.save()

                    player.won = True
                    player.save()
                    
                    other.user.lost += 1
                    other.user.save()
                    
                    game.finished = True
                    game.save()
                    
                    return True

        # draw
        if all(all(row) for row in game.board):
            other = self._get_second_player(game, player)
            
            player.user.draws += 1
            player.user.save()
            
            other.user.draws += 1
            other.user.save()
            
            game.finished = True
            game.draw = True
            game.save()
            
            return True
                
        return False
        
    def get(self, request, pk):
        game = Game.objects.get(pk=pk)
        moves = Move.objects.all().filter(game=game)
        
        serializer = MoveSerializer(moves, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, pk):
        game = Game.objects.get(pk=pk)
        player = request.user.player_set.filter(game=game)
                
        if not player:
            return Response(const.ERROR_NOT_IN_GAME, status=status.HTTP_400_BAD_REQUEST)
        
        if not game.started:
            return Response(const.ERROR_GAME_NOT_ACTIVE, status=status.HTTP_400_BAD_REQUEST)
        
        player = player.get()
                
        if player.pk == game.now_turn:
            x = int(request.data.get('x'))
            y = int(request.data.get('y'))
            try:
                if game.board[x][y]:
                    return Response(const.ERROR_SPOT_TAKEN, status=status.HTTP_400_BAD_REQUEST)
            except IndexError:
                return Response(const.ERROR_INVALID_MOVE, status=status.HTTP_400_BAD_REQUEST)
            
            data = {'x': x,
                    'y': y,
                    'player': player.pk}
            
            move = MoveSerializer(data=data, context={'player': player.pk, 'game': game.pk})
            if move.is_valid():
                move.save()
                self._make_move(x, y, game, player)
                self._check_winning_conditions(game, player)
                
                serializer = GameSerializer(game)
                
                return Response({'game': serializer.data,
                                 'move': move.data},
                                 status=status.HTTP_200_OK
                                 )
        else:
            return Response(const.ERROR_NOT_TURN, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({}, status=status.HTTP_404_NOT_FOUND)


class GameLastMove(APIView):
    def get(self, request, pk):
        game = Game.objects.get(pk=pk)
        moves = Move.objects.all().filter(game=game)
        
        serializer = MoveSerializer(moves.first())
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
