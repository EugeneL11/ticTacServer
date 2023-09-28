# ticTacToeServer

Tic-Tac-Toe client code that connects to the exisiting server so that the user can play the game.
It takes in two extra command line arguments, first one as HOST and second one as PORT. If they are wrong or not provided, I reprompt the user until it is correct. 
When started, user is prompted with the menu to make a choice, which are Play a new game, Load a saved game, Show score, and Exit. The user is shown numbers from 
1-4 that represent each choice. If an invalid choice is inputted, they'll be reprompted until it is valid. While playing the game, the user is shown the board and
their piece. They can choose to play, where my board is represented from rows 1-3 and columns 1-3. I changed it from 0-2 into 1-3 as I believe it is more intuitive. 
If they win, lose, or tie, they will be told that it happened. They can choose to save at any moment to a file name of their choice, where they will then be stored
to be loaded later into a subdirectory called 'savedGames' located in the working directory of the python code. They can also end the game at any time. The saved games
can be loaded from the menu option, and the current record can also be viewed. If exit is selected, the connection to the server is closed, and the program is exited,
and all the saved game files are also deleted. 