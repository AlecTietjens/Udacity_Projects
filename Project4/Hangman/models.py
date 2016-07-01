"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

import random
import logging
from datetime import date
from protorpc import messages
from google.appengine.ext import ndb


class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email =ndb.StringProperty()


class Game(ndb.Model):
    """Game object"""
    word = ndb.StringProperty(required=True)
    attempts_allowed = ndb.IntegerProperty(required=True)
    attempts_remaining = ndb.IntegerProperty(required=True, default=13)
    game_status = ndb.StringProperty(required=True, default='Playing')
    letters_guessed = ndb.StringProperty(repeated=True)
    letters_current = ndb.StringProperty(repeated=True)
    letters_remaining = ndb.IntegerProperty(required=True)

    @classmethod
    def new_game(cls, user_key, random_word):
        """Creates and returns a new game"""
        attempts = 13
        letters_current = ["" for i in range(len(random_word))]
        letters_remaining = len(random_word)
        game = Game(parent=user_key,
                    word=random_word,
                    attempts_allowed=attempts,
                    attempts_remaining=attempts,
                    letters_current=letters_current,
                    letters_remaining=len(random_word))
        game.put()
        return game

    def to_form(self, message=None):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.user_name = self.key.parent().get().name
        form.game_status = self.game_status
        form.attempts_remaining = self.attempts_remaining
        form.message = message
        form.letters_current = self.letters_current
        form.letters_guessed = self.letters_guessed
        form.letters_remaining = self.letters_remaining
        return form

    def get_score(self):
        """Get the score for the game"""
        letters = []
        letters_score = 0;
        for letter in self.word:
            if ''.join(letters).find(letter) is -1:
                letters_score = letters_score + 1
            letters.append(letter);
        return len(self.letters_guessed) - letters_score
        

    def end_game(self, won=False):
        """Ends the game - if won is True, the player won. - if won is False,
        the player lost."""
        if won:
            self.game_status = 'Won'
        else:
            self.game_status = 'Lost'
        self.put()
        # Add the game to the score 'board'
        score = Score(parent=self.key, 
                      user=self.key.parent(), 
                      date=date.today(), 
                      won=won,
                      guesses=self.attempts_allowed - self.attempts_remaining, 
                      score = self.get_score())
        score.put()


class Score(ndb.Model):
    """Score object"""
    user = ndb.KeyProperty(required=True, kind='User')
    date = ndb.DateProperty(required=True)
    won = ndb.BooleanProperty(required=True)
    guesses = ndb.IntegerProperty(required=True)
    score = ndb.IntegerProperty(required=True)

    def to_form(self):
        return ScoreForm(user_name=self.user.get().name, won=self.won,
                         date=str(self.date), guesses=self.guesses, score=self.score)
                         

class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    attempts_remaining = messages.IntegerField(2, required=True)
    game_status = messages.StringField(3, required=True)
    message = messages.StringField(4, required=False)
    user_name = messages.StringField(5, required=True)
    letters_current = messages.StringField(6, required=False, repeated=True)
    letters_guessed = messages.StringField(7, required=False, repeated=True)
    letters_remaining = messages.IntegerField(8, required=True)


class GameForms(messages.Message):
    """Return multiple GameForms"""
    items = messages.MessageField(GameForm, 1, repeated=True)
    

class NewGameForm(messages.Message):
    """Used to create a new game"""
    user_name = messages.StringField(1, required=True)


class GuessLetterForm(messages.Message):
    """Used to make a move in an existing game"""
    guess = messages.StringField(1, required=True)


class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    user_name = messages.StringField(1, required=True)
    date = messages.StringField(2, required=True)
    won = messages.BooleanField(3, required=True)
    guesses = messages.IntegerField(4, required=True)
    score = messages.IntegerField(5, required=True)


class ScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)


class UserRankingForm(messages.Message):
    """Outbound user rankings"""
    user = messages.StringField(1, required=True)
    avg_score = messages.FloatField(2, required=True)


class UserRankingForms(messages.Message):
    """Return multiple UserRankingForms"""
    items = messages.MessageField(UserRankingForm, 1, repeated=True)


class HistoryForm(messages.Message):
    """Return a move/history"""
    attempt_number = messages.IntegerField(1, required=True)
    letter_guessed = messages.StringField(2, required=True)
    guess_status = messages.StringField(3, required=True)
    game_status = messages.StringField(4, required=False)
    
    
class GameHistoryForm(messages.Message):
    """Return multiple HistoryForms for game history"""
    items = messages.MessageField(HistoryForm, 1, repeated=True)
    
    
class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)


