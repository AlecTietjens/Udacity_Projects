#Full Stack Nanodegree Project 4 - Hangman API

## Set-Up Instructions:
1.  Update the value of application in app.yaml to the app ID you have registered
 in the App Engine admin console and would like to use to host your instance of this sample.
2.  Run the app with the devserver using dev_appserver.py DIR, and ensure it's
 running by visiting the API Explorer - by default localhost:8080/_ah/api/explorer.
3.  (Optional) Generate your client library(ies) with the endpoints tool.
 Deploy your application.
 
 
 
##Game Description:
Hangman is a simple letter guessing game. Each game begins with a random word
that comes from a selection in the dictionary.py file. Users guesses are sent to
the `make_move` endpoint which will reply with a message letting the user know if
their guess is incorrect or correct and the status of the game.
Many different Hangman games can be played by many different users at any
given time. Each game can be retrieved or played by using the path parameter
`urlsafe_game_key`.

##Files Included:
 - api.py: Contains endpoints and game playing logic.
 - app.yaml: App configuration.
 - cron.yaml: Cronjob configuration.
 - main.py: Handler for taskqueue handler.
 - models.py: Entity and message definitions including helper methods.
 - utils.py: Helper function for retrieving ndb.Models by urlsafe Key string.
 - dictionary.py: contains a helper method and all the words that can be used in the game.

##Endpoints Included:
 - **cancel_game**
 	- Path: 'game/cancel/{urlsafe_game_key}'
 	- Method: PUT
 	- Parameters: urlsafe_game_key
 	- Description: Cancels requested game if it is still in play.

 - **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: user_name, email (optional)
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. user_name provided must be unique. Will 
    raise a ConflictException if a User with that user_name already exists.
    
 - **get_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameForm with current game state.
    - Description: Returns the current state of a game.
       
 - **get_game_history**
 	- Path: 'gamehistory/{urlsafe_game_key}
 	- Method: GET
 	- Parameters: urlsafe_game_key
 	- Description: Gets history of moves for completed game, with the last guess showing
 	the status of the game
    
 - **get_high_scores**
 	- Path: 'highscores'
 	- Method: GET
 	- Parameters: number_of_results (optional)
 	- Description: Get ordered high scores for hangman. Optional parameter will decide 
 	how many results to show, and if no parameter is provided all results will show.
 	
 - **get_scores**
    - Path: 'scores'
    - Method: GET
    - Parameters: None
    - Returns: ScoreForms.
    - Description: Returns all Scores in the database (unordered).
    
 - **get_user_games**
 	- Path: 'games/{user_name}'
 	- Method: GET
 	- Parameters: user_name, email (optional)
 	- Description: Get all games for user specified (unordered).
 	
 - **get_user_rankings**
 	- Path: 'userrankings'
 	- Method: GET
 	- Parameters: None
 	- Description: Returns all users ordered from 0 up by average score from their games.
 
 - **get_user_scores**
    - Path: 'scores/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: ScoreForms. 
    - Description: Returns all Scores recorded by the provided player (unordered).
    Will raise a NotFoundException if the User does not exist.
 	
 - **guess_letter**
    - Path: 'game/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key, guess
    - Returns: GameForm with new game state.
    - Description: Accepts a 'guess' and returns the updated state of the game.
    If this causes a game to end, a corresponding Score entity will be created.
 	
 - **new_game**
    - Path: 'game'
    - Method: POST
    - Parameters: user_name
    - Returns: GameForm with initial game state.
    - Description: Creates a new Game. user_name provided must correspond to an
    existing user - will raise a NotFoundException if not.

##Models Included:
 - **User**
    - Stores unique user_name and (optional) email address.
    
 - **Game**
    - Stores unique game states. Associated with User model via KeyProperty.
    
 - **Score**
    - Records completed games. Associated with Users model via KeyProperty.
    
##Forms Included:
 - **GameForm**
    - Representation of a Game's state (urlsafe_key, attempts_remaining,
    game_over flag, message, user_name).
 - **GameForms**
 	- Multiple GameForm container.
 - **NewGameForm**
    - Used to create a new game (user_name, min, max, attempts)
 - **GuessLetterForm**
    - Inbound make move form (guess).
 - **ScoreForm**
    - Representation of a completed game's Score (user_name, date, won flag,
    guesses).
 - **ScoreForms**
    - Multiple ScoreForm container.
 - **UserRankingForm**
 	- Used in response for user rankings - holds their average score and username.
 - **UserRankingsForm**
 	- Multiple UserRankingForm container.
 - **HistoryForm**
 	- Used in response to game history - holds the move status, letter guessed, guess
 	status, and game status.
 - **GameHistoryForm**
 	- Multiple HistoryForm container.
 - **StringMessage**
    - General purpose String container.