"""api.py - Create and configure the Game API exposing the resources.
This can also contain game logic. For more complex games it would be wise to
move game logic to another file. Ideally the API will be simple, concerned
primarily with communication to/from the API's users."""

import logging
import endpoints
import dictionary
import re
from protorpc import remote, messages
from google.appengine.api import memcache
from google.appengine.api import taskqueue

from models import User, Game, Score
from models import StringMessage, NewGameForm, GameForm, GuessLetterForm,\
    ScoreForms, GameForms, UserRankingForm, UserRankingForms, HistoryForm, GameHistoryForm
from utils import get_by_urlsafe

NEW_GAME_REQUEST = endpoints.ResourceContainer(NewGameForm)
GET_GAME_REQUEST = endpoints.ResourceContainer(urlsafe_game_key=messages.StringField(1),)
GUESS_LETTER_REQUEST = endpoints.ResourceContainer(
    GuessLetterForm,
    urlsafe_game_key=messages.StringField(1),)
USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1),
                                           email=messages.StringField(2),)
HIGH_SCORES = endpoints.ResourceContainer(number_of_results=messages.IntegerField(1))

USER_RANKINGS = endpoints.ResourceContainer()

MEMCACHE_MOVES_REMAINING = 'MOVES_REMAINING'

@endpoints.api(name='hangman', version='v1')
class HangmanApi(remote.Service):
    """Hangman API"""
    @endpoints.method(request_message=USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                    'A User with that name already exists!')
        user = User(name=request.user_name, email=request.email)
        user.put()
        return StringMessage(message='User {} created!'.format(
                request.user_name))

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new game"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        """Only start a game if none exist or if all have been finished"""
        games = Game.query(ancestor=user.key)
        if games is not None:
            for game in games.iter():
                if game.game_status == 'Playing':
                    raise endpoints.BadRequestException(
                            'A game is already going for the user!')
        
        game = Game.new_game(user.key, dictionary.get_random_word())
        # Use a task queue to update the average attempts remaining.
        # This operation is not needed to complete the creation of a new game
        # so it is performed out of sequence.
        # taskqueue.add(url='/tasks/cache_average_attempts')
        return game.to_form('Good luck playing Hangman!')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            if game.game_status == 'Playing':
                return game.to_form('Guess a letter!')
            else:
                return game.to_form('This game is completed!')
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/cancel/{urlsafe_game_key}',
                      name='cancel_game',
                      http_method='PUT')
    def cancel_game(self, request):
        """Cancel a game"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            if game.game_status == 'Playing':
                game.game_status = 'Cancelled'
                game.put()
                return game.to_form('Game has been cancelled!')
            else:
                return game.to_form('Unable to cancel game!')
        else:
            raise endpoints.NotFoundException('Game not found!')

    @endpoints.method(request_message=GUESS_LETTER_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='guess_letter',
                      http_method='PUT')
    def guess_letter(self, request):
        """Makes a move. Returns a game state with message"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game.game_status != 'Playing':
            return game.to_form('Game already over!')

        guess = request.guess.lower()

        if re.match(r"[^a-z]|[a-z]{2,}", guess):
            raise endpoints.BadRequestException(
                    'You need to guess one letter!')
        
        if guess in game.letters_guessed:
            raise endpoints.ConflictException(
                    'You\'ve already guessed that letter!')

        for i in range(len(game.word)):
            if guess == game.word[i]:
                game.letters_current[i] = guess
                game.letters_remaining -= 1
        
        game.attempts_remaining -= 1
        game.letters_guessed.append(guess)

        if game.letters_remaining < 1:
            game.end_game(True)
            msg = 'You just won!'
        elif game.attempts_remaining < 1:
            game.end_game(False)
            msg = 'You just ran out of guesses!'
        else:
            msg = 'Nice guess!'
            
        game.put()

        return game.to_form(msg)

    @endpoints.method(response_message=ScoreForms,
                      path='scores',
                      name='get_scores',
                      http_method='GET')
    def get_scores(self, request):
        """Return all scores"""
        return ScoreForms(
                items=[score.to_form() for score in Score.query()])

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=ScoreForms,
                      path='scores/{user_name}',
                      name='get_user_scores',
                      http_method='GET')
    def get_user_scores(self, request):
        """Returns all of an individual User's scores"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        scores = Score.query(Score.user == user.key)
        return ScoreForms(items=[score.to_form() for score in scores])

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=GameForms,
                      path='games/{user_name}',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """Get the games for the logged in user"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        games = Game.query(Game.game_status=="Playing", ancestor=user.key)
        return GameForms(items=[game.to_form() for game in games])

    @endpoints.method(request_message=HIGH_SCORES,
                      response_message=ScoreForms,
                      path='highscores',
                      name='get_high_scores',
                      http_method='GET')
    def get_high_scores(self, request):
        """Gets the high scores for the game"""
        if request.number_of_results is not None:
            scores = Score.query().order(Score.score).fetch(request.number_of_results)
        else:
            scores = Score.query().order(Score.score)
        return ScoreForms(items=[score.to_form() for score in scores])

    @endpoints.method(response_message=UserRankingForms,
                      path='userrankings',
                      name='get_user_rankings',
                      http_method='GET',)
    def get_user_rankings(self, request):
        """Gets user rankings"""
        users = User.query()
        forms = []
        for user in users:
            scores = Score.query(Score.user==user.key)
            if scores.get() is not None:
                scores = [float(score.score) for score in scores]
                avg_score = sum(scores)/len(scores)
                form = UserRankingForm()
                form.user = user.name
                form.avg_score = avg_score
                forms.append(form)            
        return UserRankingForms(items=sorted(forms, key=lambda form: form.avg_score))

    @endpoints.method(response_message=GameHistoryForm,
                      request_message=GET_GAME_REQUEST,
                      path='gamehistory/{urlsafe_game_key}',
                      name='get_game_history',
                      http_method='GET',)
    def get_game_history(self, request):
        """Gets history of moves for a game"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        
        if game.game_status == 'Playing':
            return game.to_form('Game has not finished!')
        
        # initialize variables
        guesses = game.letters_guessed
        count = 1
        forms = []
        
        # go through all letters guessed except last one
        for letter in guesses:
            form = HistoryForm()
            if ''.join(game.word).find(letter) is -1:
                form.guess_status = 'Incorrect'
            else:
                form.guess_status = 'Correct'
            form.letter_guessed = letter
            form.attempt_number = count
            count = count + 1
            forms.append(form)
        
        # attach game status to last move/form
        forms[-1].game_status = game.game_status
            
        return GameHistoryForm(items = forms)


api = endpoints.api_server([HangmanApi])