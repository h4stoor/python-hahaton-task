EMPTY_BOARD = [
    [None for _ in range(15)] for __ in range(15)
]

OWNER = 'o'
GUEST = 'g'

ERROR_ALREADY_JOINED = {'error': 'You are already a player in this game.'}
ERROR_GAME_FULL = {'error': 'This game is already full.'}
ERROR_NOT_IN_GAME = {'error': 'You are not participating in this game.'}
ERROR_GAME_ACTIVE = {
    'error': 'This operation cannot be performed while game is active.'
}
ERROR_GAME_NOT_ACTIVE = {'error': 'This game is not started.'}
ERROR_NOT_TURN = {'error': "It's not your turn to move"}
ERROR_SPOT_TAKEN = {'error': 'This spot is already taken.'}
ERROR_INVALID_MOVE = {'error': 'Invalid move.'}
