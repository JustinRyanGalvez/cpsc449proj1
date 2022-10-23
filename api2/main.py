import collections
import dataclasses
import sqlite3
import textwrap
import json

import databases
import toml
import random

from quart import Quart, g, request, abort
from quart_schema import QuartSchema, RequestSchemaValidationError, validate_request

app = Quart(__name__)
QuartSchema(app)

app.config.from_file(f"./etc/{__name__}.toml", toml.load)

@dataclasses.dataclass
class User:
    username: str
    password: str

@dataclasses.dataclass
class Game:
    game_id: int
    user_id: int
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

# Register user
@app.route("/register", methods=["POST"])
@validate_request(User)
async def register(data):
    db = await _get_db()

    # Use user class as staple for sql commands
    user = dataclasses.asdict(data)

    # Insert user info in user table
    try:
        id = await db.execute(
            "INSERT INTO user(username, password) VALUES (:username, :password)",
            user
        )
    except sqlite3.IntegrityError as e:
        abort(409, e)

    user["id"] = id
    return user, 201, {"Location": f"/users/{id}"}

@app.route("/basic-auth/<string:user>/<string:passwd>", methods=["GET"])
async def authenticate(user, passwd):
    db = await _get_db()

    # Grab username and password from db
    userid = await db.fetch_one(
        """
        SELECT *
        FROM user
        WHERE username = :user
        AND password = :passwd
        """,
        values={"user" : user, "passwd" : passwd}
    )

    if userid:
        return { "authenticated": True }, 200
    else:
        return{"error":"could not verify user"}, 401, {'WWW-Authenticate': 'Basic realm="User Visible Realm"'}

# Create new game
@app.route("/games/new/", methods=["POST"])
@validate_request(newGame)
async def create_game(data):

    db = await _get_db()

    # Initialize class newGame as dictionary using data in POST command
    newgame = dataclasses.asdict(data)

    # Create new game in game table
    try:
        id = await db.execute(
            """
            INSERT INTO game(user_id, word_id)
            VALUES ((SELECT user_id FROM user WHERE user_id = :user_id), (SELECT word_id FROM correct_answers ORDER BY RANDOM() LIMIT 1))
            """,
            newgame,
        )

    except sqlite3.IntegrityError as e:
        abort(409, e)

    newgame["game_id"] = id
    return newgame, 201, {"Location": f"/game/{id}"}

# Play game
@app.route("/play", methods=["PATCH"])
@validate_request(Game)
async def play_game(data):
    db = await _get_db()

    # Transforms game into dictionary from dataclass
    game = dataclasses.asdict(data)

    # Initialize variables
    user_id = game["user_id"]
    game_id = game["game_id"]

    # Grab word_id tuple
    word_id = await db.fetch_one(
        """
        SELECT word_id
        FROM game
        WHERE game_id = :game_id
        """,
        values={"game_id" : game_id}
    )

    min_guess = await db.fetch_one(
        """
        SELECT MIN(guesses_left)
        FROM game_states
        WHERE game_id = :game_id
        AND user_id = :user_id
        """,
        values={"game_id" : game_id, "user_id" : user_id},
    )

    minimum_guess = min_guess[0]

    condition = await db.fetch_one(
        """
        SELECT condition
        FROM game_states
        WHERE game_id = :game_id
        AND user_id = :user_id
        AND guesses_left = :minimum_guess
        """,
        values={"game_id" : game_id, "user_id" : user_id, "minimum_guess" : minimum_guess},
    )

    current_condition = condition[0]

    # Initialize more variables
    word_id = word_id[0]
    guess = game["guess"]

    # Grab guesses_left to check condition
    guesses_left = await db.fetch_one(
        """
        SELECT guesses_left
        FROM game
        WHERE game_id = :game_id
        AND user_id = :user_id
        """,
        values={"game_id" : game_id, "user_id" : user_id},
    )

    if guesses_left[0] == 0 or current_condition == 'W':
        return {"error" : "Game was terminated"}

    # Grabs secret word for comparing later
    secret_word = await db.fetch_one(
        """
        SELECT answers
        FROM correct_answers
        WHERE word_id = (SELECT word_id FROM game WHERE game_id = :game_id)
        """,
        values={"game_id": game_id},
    )

    # Grab all possible answers from db
    correct_answers = await db.fetch_all("SELECT answers FROM correct_answers")
    possible_answers = await db.fetch_all("SELECT answers FROM possible_answers")
    counter = 0

    for i in range(len(correct_answers)):
        if guess == correct_answers[i][0]:
            counter = 1
            guess_valid = 'True'

    # Check if guess is valid by comparing it to every possible answer
    for i in range(len(possible_answers)):
        if guess == possible_answers[i][0]:
            counter = 1
            guess_valid = 'True'

    if counter == 1:

        # If winning condition, update condition
        if guess == secret_word[0]:
            # update condition
            id = await db.execute(
                "UPDATE game SET condition = 'W' WHERE game_id = :game_id AND user_id = :user_id",
                values={"game_id" : game_id, "user_id" : user_id}
            )
            condition = 'W'
            correctSpot = guess
            wrongSpot = ''
            game["guess_valid"] = guess_valid
            game["guesses_left"] = guesses_left[0]
            game["correct_spot"] = guess
            game["wrong_spot"] = ''
            game["condition"] = 'W'
            id = await db.execute(
                """
                INSERT INTO game_states(game_id, user_id, word_id, guess, guess_valid, guesses_left, correct_spot, wrong_spot, condition)
                VALUES(:game_id, :user_id, (SELECT word_id FROM game WHERE user_id = :user_id), :guess, :guess_valid, :guesses_left, :correct_spot, :wrong_spot, :condition)
                """,
                values={"game_id" : game_id, "user_id" : user_id, "guess" : guess, "guess_valid" : guess_valid, "guesses_left" : guesses_left[0], "correct_spot" : correctSpot, "wrong_spot" : wrongSpot, "condition" : condition},
            )
            return game, 200, {"Location": f"/games/{id}"}

        # Place guess letters in list for easier manipulation
        correctSpotList = []
        wrongSpotList = []

        # Compare each letter and see if it is in secret word
        for x in range(0, len(secret_word[0])):
            for y in range(0, len(secret_word[0])):
                if guess[x] == secret_word[0][y] and x == y:
                    correctSpotList.append(guess[x])

                elif guess[x] == secret_word[0][y] and x != y:
                    wrongSpotList.append(guess[x])

        # Make lists into strings
        correctSpot = ''.join(correctSpotList)
        wrongSpot = ''.join(wrongSpotList)

        # Decrement guesses_left
        id = await db.execute(
            """
            UPDATE game
            SET guesses_left = guesses_left - 1
            WHERE game_id = :game_id
            """,
            values={"game_id" : game_id}
        )

        # Grab guesses_left for condition
        guesses_left = await db.fetch_one(
            """SELECT guesses_left
            FROM game
            WHERE game_id = :game_id
            """,
            values={"game_id": game_id}
        )

        # Update dictionary values to send to user
        game["guess_valid"] = guess_valid
        game["guesses_left"] = guesses_left[0]
        game["correct_spot"] = correctSpot
        game["wrong_spot"] = wrongSpot

        # If no more guesses, condition becomes L
        if guesses_left[0] == 0:
            game["condition"] = "L"
            x = await db.execute(
                """
                UPDATE game
                SET condition = 'L'
                WHERE game_id = :game_id
                """,
                values={"game_id" : game_id}
            )
            condition = game["condition"]
        else:
            game["condition"] = "IP"
            condition = game["condition"]

        # Insert all info user received into game_states for later requests
        id = await db.execute(
            """
            INSERT INTO game_states(game_id, user_id, word_id, guess, guess_valid, guesses_left, correct_spot, wrong_spot, condition)
            VALUES(:game_id, :user_id, (SELECT word_id FROM game WHERE user_id = :user_id), :guess, :guess_valid, :guesses_left, :correct_spot, :wrong_spot, :condition)
            """,
            values={"game_id" : game_id, "user_id" : user_id, "guess" : guess, "guess_valid" : guess_valid, "guesses_left" : guesses_left[0], "correct_spot" : correctSpot, "wrong_spot" : wrongSpot, "condition" : condition},
        )
        return game, 200, {"Location": f"/games/{id}"}

    else:
        return {"error": "Guess was not a possible answer"}, 404

# Grab games of user
@app.route("/games/<int:user_id>", methods=["GET"])
async def grab_games(user_id):
    db = await _get_db()

    # Grab all games from game table
    game = await db.fetch_one(
        "SELECT * FROM game WHERE user_id = :user_id",
        values={"user_id": user_id}
    )
    if game:
        return dict(game)
    else:
        return {"error": "Games were not found"}, 404

# Grab game state
@app.route("/games/<int:game_id>/<int:user_id>", methods=["GET"])
async def grab_game_state(game_id):
    db = await _get_db()

    # Grab game_state from game_state table and return as dictionary to user
    game_state = await db.fetch_one(
        """
        SELECT *
        FROM game_state
        WHERE game_id = :game_id
        AND user_id = :user_id
        """,
        values={"game_id" : game_id, "user_id" : user_id}
    )

    if game_state:
        return dict(game_state)
    else:
        return {"error": "Game state was not found"}, 404
        abort(404)

@app.errorhandler(RequestSchemaValidationError)
def bad_request(e):
    return {"error": str(e.validation_error)}, 400


@app.errorhandler(409)
def conflict(e):
    return {"error": str(e)}, 409
