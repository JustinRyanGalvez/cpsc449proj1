import collections
import dataclasses
import sqlite3
import textwrap
import json

import databases
import toml

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
    id: int
    user_id: string
    word_id: int

async def _connect_db():
    database = databases.Database(app.config["DATABASES"]["URL"])
    await database.connect()
    return database


def _get_db():
    if not hasattr(g, "sqlite_db"):
        g.sqlite_db = _connect_db()
    return g.sqlite_db


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


@app.route("/games/all", methods=["GET"])
async def all_books():
    db = await _get_db()
    all_games = await db.fetch_all("SELECT * FROM games;")
    return list(map(dict, all_games))

@app.route("/games/<int:id>/<string:user_id>", methods=["GET"])
async def one_game(id, user_id):
    db = await _get_db()
    game = await db.fetch_one("SELECT * FROM games WHERE id = :id AND user_id = :user_id, values={"id": id})
    if game:
        return dict(game)
    else:
        abort(404)

# Ask Carter where correct word is stored and fix line with hashtags
@app.route("/games/<int:id>/<string:user_id>", methods=["PUT"])
async def one_book(id, user_id):
    db = await _get_db()
    game = await db.fetch_one("SELECT * FROM games WHERE id = :id AND user_id = :user_id, values={"id": id}) #######
    if game:
        return dict(game)
    else:
        abort(404)

@app.route("/games/new/", methods=["POST"])
@validate_request(Game)
def create_game(data):
    db = await _get_db()
    game = dataclasses.asdict(data)
    try:
        id = await db.execute(
            """
            INSERT INTO games(id, user_id, word_id)
            VALUES(:id, :user_id, :word_id)
            """,
            game,
        )
    except sqlite3.IntegrityError as e:
        abort(409, e)

    game["id"] = id
    return game, 201, {"Location": f"/games/{id}"}

@app.route("/scores/all", methods=["GET"])
async def all_scores():
    db = await _get_db()
    all_scores = await db.fetch_all("SELECT * FROM scores;")
    return list(map(dict, all_scores))

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
