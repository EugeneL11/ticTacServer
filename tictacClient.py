# CPSC 441 Assignment 1
# Eugene Lee - 30137489

# Necessary imports
import sys
import socket as soc
import os

# A set of variables to be used that I need to initialize
wCount = 0
lCount = 0
tCount = 0
brdMsg = ""
fileList = []
subdir = "./savedGames" 
symbolTrack = ""

def boardConverter(boardMsg): #Convert the single-line message form of the game into a readable tic tac toe board
    boardNums = ''.join(char for char in boardMsg if char.isdigit()) #Cut out all letters and punctuations
    global symbolTrack #Keep track of which symbol the user is
    twoCount = 0
    for char in boardNums: #Keep track of the number of empty spaces
        if char == "2":
            twoCount += 1
    if twoCount % 2 == 0: #AI always plays immediately after the user so if there are even empty spaces, it means the user started second
        symbolTrack = "O"
    else:
        symbolTrack = "X" #if there are odd empty spaces, the user started first
    print(f"Your piece is: {symbolTrack}") #let the user know which piece theirs
    boardNums = boardNums.replace("2", " ").replace("1", "O").replace("0", "X") #Make it readable
    print(f"|{boardNums[0]}|{boardNums[1]}|{boardNums[2]}|\n" #formatting the board
        + f"|{boardNums[3]}|{boardNums[4]}|{boardNums[5]}|\n"
        + f"|{boardNums[6]}|{boardNums[7]}|{boardNums[8]}|\n")

def move(playPrompt): #Taking in user input to choose where to place a piece
    while True: #this loop will ensure that the input is valid
        if len(playPrompt) == 3: #condition separated to avoid improper indexing of string
            if (playPrompt[0] in ["1", "2", "3"]) and (playPrompt[1] == ",") and (playPrompt[2] in ["1", "2", "3"]): #must be the correct index
                break
            else: #if input is in wrong format
                playPrompt = input("Invalid input! Please enter in 'row,column' format of values 1, 2, or 3 (ex.'2,3'): ") #re-prompt 
        else: #if input is longer than 3 chars
            playPrompt = input("Invalid input! Please enter in 'row,column' format of values 1, 2, or 3 (ex.'2,3'): ") #re-prompt 
    playPrompt = playPrompt.replace(",", "")
    return (f"MOVE:{int(playPrompt[0])-1},{int(playPrompt[1])-1}") #formatting as the network protocol

def playOptions(startPrompt): #user options once new game starts
    if startPrompt == "P": #Playing a move in the game
        playStart = input("Enter where you would like to place your piece in a 'row,column' format (1, 2, or 3): ")
        playMessage = move(playStart) #place and error-check
        try: 
            s.sendall(playMessage.encode('utf-8')) #handling possible socket errors
            response = s.recv(1020)
        except soc.error as e:
            print("Error sending/receiving data to server: {e}")
            sys.exit(1)
        responseD = response.decode()
        while responseD[:4] == "EROR": #if the server sends an error, the space is occupied
            newPlayPrompt = input("This space is occupied! Please enter a new location in a 'row,column' format (1, 2, or 3): ")
            playMessage = move(newPlayPrompt) #retry
            try: 
                s.sendall(playMessage.encode('utf-8'))
                response = s.recv(1020)
            except soc.error as e:
                print("Error sending/receiving data to server: {e}")
                sys.exit(1)
            responseD = response.decode()
        global brdMsg
        brdMsg = responseD #used to keep track of the board message
        if responseD[:4] == "UWIN": #Handle the win
            print("\nThe game has ended!\nCongratulations, you won!  Great job :)")
            global wCount
            wCount += 1 #for show score
            gameplay(s) #show the menu again since game is over now
        boardConverter(responseD)
        if responseD[:4] == "OVER": #if the server indicates game is over
            print("The game has ended!")
            if responseD[5] == "C":
                print("Congratulations, you won!  Great job :)")
                wCount += 1 #for show score
            elif responseD[5] == "S" :
                print("You have unfortunately lost :(  Maybe try again?")
                global lCount
                lCount += 1 #for show score
            else:
                print("It is a tie, I believe that you can win next time...")
                global tCount
                tCount += 1 #for show score
            gameplay(s) #show the menu again since game is over now
        else:
            play() #so that it keeps playing if game isn't over yet

    elif startPrompt == "E": #Ending the game
        try: 
            s.sendall(b"ENDG") #tell the server the game ended
            response = s.recv(1020)
        except soc.error as e:
            print("Error sending/receiving data to server: {e}")
            sys.exit(1)
        
        print("Game Over! There is no winner :(\nThis is where the game was stopped at: ")
        boardConverter(response.decode()) #show the board
        gameplay(s) #menu options

    elif startPrompt == "S": #Saving the game to be loaded later
        brdMsg2 = brdMsg[5:] #getting just the location content of board
        if brdMsg2 == "": #Since the brdMsg's value first gets set in P
            brdMsg2 = "2,2,2,2,2,2,2,2,2"
        loadBoard = f"LOAD:{symbolTrack}," + brdMsg2 #make into LOAD network protocol message
        saveFileName = input("Save the file as: ")
        os.makedirs(subdir, exist_ok=True) #Ensure subdir exists and create it if it doesn't
        full_path = os.path.join(subdir, saveFileName) # combine subdir and filename to get the full path

        try: # Save the data to the file
            with open(full_path, "w") as file:
                file.write(loadBoard) #Write the board data
            fileList.append(saveFileName) #to be used when loading
            print(f"Data saved to {full_path}")
        except Exception as e:
            print(f"Error saving data: {e}")
        gameplay(s) #menu options

def play(): #beginning of the user's choices
    startPrompt = input("Press 'P' to play, 'E' to end the game, or 'S' to save: ")
    while True: #this loop will ensure that the input is valid
        if startPrompt in ["P", "E", "S"]:
            break
        else: 
            startPrompt = input("Invalid input! Please enter either 'P', 'E', or 'S': ") #re-prompt
    playOptions(startPrompt) #Continue with the right value

def gameplay(s): #display menu and handle menu choices
    print("\nMENU:\n"
        + " - New Game          (Press '1')\n" 
        + " - Load Saved Game   (Press '2')\n"
        + " - Show Score        (Press '3')\n"
        + " - Exit              (Press '4')\n")
    choice = input("Choose an Option: ")

    while True: #To loop on invalid inputs
        if choice == "1": #Starting a new game
            print("\nNew Game Started")
            try: 
                s.sendall(b"NEWG") #Send that new game started to server
                response = s.recv(1020)
            except soc.error as e:
                print("Error sending/receiving data to server: {e}") #Catching potential socket errors
                sys.exit(1)
            boardConverter(response.decode()) #display board
            play() #user options
            break
        elif choice == "2": #Loading a previously saved game
            loadFileName = input("\nWhich file would you like to load: ")
            loadFilePath = os.path.join(subdir, loadFileName) #full file path
            if loadFileName in fileList: #if it's a file I've saved before
                with open(loadFilePath, "r") as file: 
                    loadedData = file.read() #it will read the LOAD: message
                try: 
                    s.sendall(loadedData.encode('utf-8'))
                    response = s.recv(1020) #A BORD message
                except soc.error as e:
                    print("Error sending/receiving data to server: {e}")
                    sys.exit(1)
                responseD = response.decode()
                boardConverter(responseD)
                playOptions("P") #play a move on the loaded board
            else:
                print("Invalid file name, no such file exists...")
            gameplay(s)
            break
        elif choice == "3": #Showing the score up until this point in this session
            print(f"\nSCORE: \nWIN - {wCount} / LOSS - {lCount} / TIE - {tCount}")
            gameplay(s) #back to menu
            break
        elif choice == "4": #Close the server and exit the game
            try: 
                s.sendall(b"CLOS") #Close the server
            except soc.error as e:
                print("Error sending data to server: {e}")
                sys.exit(1)
            try: #deleting all the saved game files once server closes
                for file in os.listdir(subdir):
                    filePath = os.path.join(subdir, file)
                    if os.path.isfile(filePath):
                        os.remove(filePath)
            except Exception as e:
                if len(fileList) > 0:
                    print(f"Error deleting files: {e}")
            print("\nThank you for playing! Exiting out of the server...\n")
            sys.exit(0) #Close the whole program
        else: #Handling wrong inputs by re-prompting
            choice = input("\nPlease choose a valid option ('1', '2', '3', or '4'): ")
        

#MAIN

if len(sys.argv) == 1: #if neither HOST or PORT were provided
    hostVal = input("No IP address for the server was inputted! Please try again: ")
    HOST = hostVal
    portVal = input("No port number was inputted! Please try again: ")
    PORT = portVal
elif len(sys.argv) == 2: #if no PORT was provided
    HOST = sys.argv[1]
    portVal = input("No port number was inputted! Please try again: ")
    PORT = portVal
else: #HOST and PORT were both provided
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
PORT = int(PORT)

#handling invalid inputs for the HOST and PORT by reprompting until they are right
if HOST != "136.159.5.25":
    newIP = input("Invalid IP address for the server was inputted! Please try again: ")
    while newIP != "136.159.5.25":
        newIP = input("Invalid IP address, try again: ")
    HOST = newIP
if PORT != 6969:
    newPrt = input("Invalid port number was inputted! Please try again: ")
    while newPrt != "6969":
        newPrt = input("Invalid port number, try again: ")
    PORT = int(newPrt)
if len(sys.argv) > 3:
        print("Too many command line arguments were provided, only two will be used!")
print(f"\nServer listening on {HOST}:{PORT}\n\nWelcome to the CPSC 441 Tic Tac Toe Server!") #if there were more than just HOST and PORT

#Socket
try: 
    with soc.socket(soc.AF_INET, soc.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
        except (soc.gaierror, soc.error) as e:
            print(f"Error connecting to server: {e}")
            sys.exit(1)
        gameplay(s) #play the game, this is what starts the whole program
except soc.error as e:
    print(f"Error creating socket: {e}")
    sys.exit(1)