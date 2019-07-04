from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_xo.processor.handler import TransactionHandler
from xo_payload import *
from xo_state   import *

class XoTransactionHandler(TransactionHandler):
    def __init__(self, namespace_prefix):
        self._namespace_prefix = namespace_prefix

    @property
    def family_name(self):
        return 'xo'

    @property
    def family_versions(self):
        return ['1.1']

    
    @property
    def namespaces(self):
        return [self._namespace_prefix]

    """
    This is the part of the process where we handle
    the business logic in the transactions. 
    """
    def apply(self, transaction, context):
        # Extraction du header / signature de la transaction

        header = transaction.header
        signer = header.signer_public_key

        # Definition de la classe XoPayload ou dans le prochain exemple AssetsPayload
        
        xo_payload = XoPayload.from_bytes(transaction.payload)
        
        # Definition de la classe XoSTate   ou dans le prochain exemple AssetsState
        
        xo_state = XoState(context)

        # Gestion des actions dans la transaction 

        if xo_payload.action == 'delete':

            game = xo_state.get_game(xo_payload.name)

            if game is None:
                raise InvalidTransaction(
                    'Invalid action: game does not exist')

            xo_state.delete_game(xo_payload.name)
        
        elif xo_payload.action == 'create':
            # Testing in the state if the payload name exists in state
            if xo_state.get_game(xo_payload.name) is not None:
                    raise InvalidTransaction(
                        'Invalid action: Game already exists: {}'.format(
                            xo_payload.name))
            # Creation of new game
            game = Game(name=xo_payload.name,
                        board="-" * 9,
                        state="P1-NEXT",
                        player1="",
                        player2="")

            xo_state.set_game(xo_payload.name, game)
            #_display("Player {} created a game.".format(signer[:6]))
            print("Player {} created a game.".format(signer[:6]))
        elif xo_payload.action == 'take':
            # Récuperation du nom du jeu depuis le state
            game = xo_state.get_game(xo_payload.name)

            
            if game is None:
                raise InvalidTransaction(
                    'Invalid action: Take requires an existing game')
            
            if game.state in ('P1-WIN', 'P2-WIN', 'TIE'):
                raise InvalidTransaction('Invalid Action: Game has ended')

            if (game.player1 and game.state == 'P1-NEXT' and
                game.player1 != signer) or \
                    (game.player2 and game.state == 'P2-NEXT' and
                        game.player2 != signer):
                raise InvalidTransaction(
                    "Not this player's turn: {}".format(signer[:6]))

            if game.board[xo_payload.space - 1] != '-':
                raise InvalidTransaction(
                    'Invalid Action: space {} already taken'.format(
                        xo_payload))

            if game.player1 == '':
                game.player1 = signer

            elif game.player2 == '':
                game.player2 = signer

            upd_board = _update_board(game.board,
                                        xo_payload.space,
                                        game.state)

            upd_game_state = _update_game_state(game.state, upd_board)

            game.board = upd_board
            game.state = upd_game_state

            xo_state.set_game(xo_payload.name, game)
            _display(
                "Player {} takes space: {}\n\n".format(
                    signer[:6],
                    xo_payload.space) +
                _game_data_to_str(
                    game.board,
                    game.state,
                    game.player1,
                    game.player2,
                    xo_payload.name))
               
        else:
            raise InvalidTransaction('Unhandled action: {}'.format(xo_payload.action))
