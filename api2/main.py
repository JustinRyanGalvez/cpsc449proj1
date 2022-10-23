import collections
import dataclasses
import sqlite3
import textwrap
import json

import databases
import toml
import random
@dataclasses.dataclass
class User:
    username: str
    password: str
from quart import Quart, g, request, abort
from quart_schema import QuartSchema, RequestSchemaValidationError, validate_request

app = Quart(__name__)
QuartSchema(app)

app.config.from_file(f"./etc/{__name__}.toml", toml.load)

#

#How to create a new game
#http POST localhost:5000/games/new/[username] username="username"

#Start server on this file
#foreman start main.py

#How to make a guess
#http PUT localhost:5000/games/[username]/[game_id] username="username" game_id="game_id" guess="guess"
#return JSON {validGuess: True, letters}
#Maybe use a list and make it a json

# @dataclasses.dataclass
# class User:
#     username: str
#     password: str


@dataclasses.dataclass
class Game:
    user_id: int
    game_id: int
    guess: str


@dataclasses.dataclass
class newGame:
    user_id: int

async def _get_db():
    db = getattr(g, "_sqlite_db", None)
    if db is None:
        db = g._sqlite_db = databases.Database(app.config["DATABASES"]["URL"])
        await db.connect()
    return db


@app.teardown_appcontext
async def close_connection(exception):
    db = getattr(g, "_sqlite_db", None)
    if db is not None:
        await db.disconnect()


@app.route("/", methods=["GET"])
def index():
    return textwrap.dedent("""
    <h1>Wordle population</h1>
    <p>A prototype API for user information of Worldle players</p>\n
    """)

#
# @app.route("/games/all", methods=["GET"])
# async def all_games():
#   db = await _get_db()
#   all_games = await db.fetch_all("SELECT * FROM games;")
#   return list(map(dict, all_games))


# Apeksha portion, include authentication with password
@app.route("/register", methods=["POST"])
@validate_request(User)
async def register(data):
    db = await _get_db()
    user = dataclasses.asdict(data)

    #if not request.authorization:
     #   return{"error":"could not verify user"}, 401, {'WWW-Authenticate': 'Basic realm="User Visible Realm"'}

    #else:
     #   auth = request.authorization
    #    user = await authenticate_user(auth.username, auth.password)
     #   if user:
      #      return { "authenticated": true },200
       # else:
        #    abort(401)

    #values={"username":username, "password": password}
    try:
        id = await db.execute("INSERT INTO user(username, password) VALUES (:username, :password)",user)
    except:
        abort(409, sqlite3.IntegrityError)
    user["id"] = id
    return user,201,{"Location": f"/users/{id}"}

    #if request.authorization:
     #   auth = request.authorization
      #  user = await authenticate_user(auth.username, auth.password)
       # if user:
        #    return { "authenticated": true },200
        #else:
         #   abort(401)

    #else:
     #   return{"error":"could not verify user"}, 401, {'WWW-Authenticate': 'Basic realm="User Visible Realm"'}

@app.route("/login/<string:username>/<string:password>", methods=["GET"])
# @validate_request(User)
async def authenticate(username, password):
    db = await _get_db()
    # user = dataclasses.asdict(data)
    print("Helloas")
    userid = await db.fetch_one("SELECT * FROM user WHERE username = :username AND password = :password", values={"username" : username, "password" : password})
    print("hi")
    print(userid)
    #values={"username":username, "password": password}
    if userid:
        return { "authenticated": True },200
    else:
        return{"error":"could not verify user"}, 401, {'WWW-Authenticate': 'Basic realm="User Visible Realm"'}

#Grab games of user
@app.route("/games/<int:user_id>", methods=["GET"])
async def grab_games(user_id):
    db = await _get_db()
    game = await db.fetch_one("SELECT * FROM game WHERE user_id = :user_id",
    values={"user_id": user_id})
    print(game)
    if game:
        return dict(game)
    else:
        abort(404)

@app.route("/games/state/<int:game_id>", methods=["GET"])
async def grab_game_state(game_id):
    db = await _get_db()
    game_state = await db.fetch_one("SELECT condition FROM game WHERE game_id = :game_id", values={"game_id" : game_id})
    if game_state:
        return dict(game_state)
    else:
        abort(404)



# Play game
@app.route("/play", methods=["PATCH"])
@validate_request(Game)
async def play_game(data):
    db = await _get_db()

    # Transforms game into dictionary from dataclass
    game = dataclasses.asdict(data)

    print('game: ', game)

    user_id = game["user_id"]
    game_id = game["game_id"]
    guess = game["guess"]
    # Check if game exists by looking at the word_id with game_id and user_id
    # word_id = await db.fetch_one(
    #   
    #     SELECT word_id
    #     FROM game
    #     WHERE :user_id
    #     AND :game_id
    #     """,
    #     game,
    # )
    # word_id = 5
    # print("word id: ", word_id)

    # if word_id:
    try:
        id = await db.execute("UPDATE game SET guess = :guess WHERE :game_id AND user_id = :user_id", game)

    except sqlite3.IntegrityError as e:
        abort(409, e)
    # # Grabs secret word for comparing later
    secret_word = await db.fetch_one(
        """
        SELECT answers
        FROM correct_answers
        WHERE word_id = (SELECT word_id FROM game WHERE game_id = :game_id)
        """,
        values={"game_id": game_id},
    )

    print("guess: ", guess)
    print("Secret word: ", secret_word[0])
    # Updates guess in db


    # If these statements don't work, make a new var and do a fetchone() from the newly
    # updated table and store the value that way
    # May not be needed
    # print("guess = ", guess)
    # game["guess"] = guess
#
#     # Grab all possible answers from db
    possible_answers = await db.fetch_all("SELECT answers FROM possible_answers")

    counter = 0
    # Check if guess is valid by comparing it to every possible answer
    for i in range(len(possible_answers)):
        if guess == possible_answers[i][0]:
            counter = 1
            guess_valid = await db.execute("UPDATE game SET guess = :guess, guess_valid = 'True' WHERE game_id = :game_id AND user_id = :user_id", game)
            print("guess valid: ", guess_valid)

#
    if counter == 1:
# #     if game["guess_valid"] == 'True':
# #
# #         # Update guess_valid in db
# #         try:
# #             guess_valid = await db.execute(
# #                 """
# #                 UPDATE game SET guess_valid = True WHERE game_id = :game_id
# #                 """,
# #                 game,
# #             )
# #
# #         except sqlite3.IntegrityError as e:
# #             abort(409, e)
# #
# #
        # If winning condition, update condition
        if guess == secret_word[0]:
            # update condition
            condition = await db.execute("UPDATE game SET condition = 'W', correct_spots = :guess WHERE game_id = :game_id AND user_id = :user_id", game)
            return game, 201, {"Location": f"/games/play"}
#
        # Place guess letters in list to be able to remove duplicates later
        # (May not be needed)
        correctSpotList = []
        wrongSpotList = []
# #
# #         # Compare each letter and see if it is in secret word
        for x in range(0, len(secret_word[0])):
            for y in range(0, len(secret_word[0])):
                if guess[x] == secret_word[0][y] and x == y:
                    correctSpotList.append(guess[x])

                elif guess[x] == secret_word[0][y] and x != y:
                    wrongSpotList.append(guess[x])
    # #
        print("correctSpotList: ", correctSpotList)
        print("wrongSpotList: ", wrongSpotList)


        # (May not be needed)
        # correctSpotList = list(dict.fromkeys(correctSpotList))
        # wrongSpotList = list(dict.fromkeys(wrongSpotList))
        #
        # # (May not be needed)
        correctSpot = ''.join(correctSpotList)
        wrongSpot = ''.join(wrongSpotList)

        print("correctSpot: ", correctSpot)
        print("wrongSpot: ", wrongSpot)
# #
#         # Update correct spot and wrong spot in db
        game["correct_spot"] = correctSpot
        game["wrong_spot"] = wrongSpot
        #try:
         #   correct_spot = await db.execute("""UPDATE game SET correct_spot = ? WHERE guess = :guess AND game_id = :game_id AND user_id = :user_id""", (correctSpot))

#            wrong_spot = await db.execute("""UPDATE game SET wrong_spot = :wrongSpot WHERE game_id = :game_id AND user_id = :user_id""", game)


       # except sqlite3.IntegrityError as e:
         #   abort(409, e)
# #
# #         # (May not be needed)
# #         game["correct_spot"] = correct_spot
# #         game["wrong_spot"] = wrong_spot
# #
#         # If not every letter in correctSpot, deduct guesses_left by 1 in db
#         if len(correctSpot) < 5:
#             try:
#                 guesses_left = await db.execute("""UPDATE game SET guesses_left = guesses_left - 1 WHERE game_id = :game_id AND user_id = :user_id""", game)
#
#             except sqlite3.IntegrityError as e:
#                 abort(409, e)
#
#             # (May not be needed)
#             # game["guesses_left"] = guesses_left
#             id = game["game_id"]
#             return game, 200, {"Location": f"/games/play/{id}"}
# #
    else:
        print("Guess was not in possible_answers")
        abort(404)

    # else:
    #     abort(404)

# Create new game
@app.route("/games/new/", methods=["POST"])
@validate_request(newGame)
async def create_game(data):
    db = await _get_db()
    newgame = dataclasses.asdict(data)
    print("game: ", game)
    try:
        id = await db.execute(
            """
            INSERT INTO game(user_id, word_id)
            VALUES (:user_id, (SELECT word_id FROM correct_answers ORDER BY RANDOM() LIMIT 1))
            """,
            game
        )

    except sqlite3.IntegrityError as e:
        abort(409, e)

    newgame["game_id"] = id
    return game, 201, {"Location": f"/game/{id}"}


# @app.route("/scores/all", methods=["GET"])
# async def all_scores():
#   db = await _get_db()
#   all_scores = await db.fetch_all("SELECT * FROM scores;")
#   return list(map(dict, all_scores))


@app.errorhandler(RequestSchemaValidationError)
def bad_request(e):
    return {"error": str(e.validation_error)}, 400


@app.errorhandler(409)
def conflict(e):
    return {"error": str(e)}, 409


# def newGame():
#   //Establish new identifier
#   id = something

#   // Grab word from database
#   word = db.get().random()

#   arr = []
#   right_letter = []

#   //Place letter in array
#   for i in len(range(word)):
#     arr.append(word[i])
#   user_try = input("Guess a 5 letter word.")

#   //Compare user word with correct word
#   for i in len(range(user_try)):
#     if user_try[i] == arr[i]:
#       print("slot ", i, " is correct")
#       right_letter.append(TRUE)
#     else
#       right_letter.append(FALSE)

#   //See if word is correct
#   for i in len(range(right_letter)):
#     if right_letter[i] == TRUE:
#       counter++
#       right_letter.pop(i)
#     if counter == 5:
#       print("The word was guessed correctly!")
