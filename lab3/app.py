from bottle import get, post, run, request, response, delete
import sqlite3


db = sqlite3.connect("lab3/movies.sqlite")
PORT=7007

@get('/ping')
def get_ping():
    response.status = 200
    return '<b>PONG</b>!'



@post('/reset')
def post_reset():
    c = db.cursor()
    c.execute(
        """
        INSERT
        INTO        theaters(theater_name, capacity)
        VALUES      ("Kino",10);
                    ("Regal",16);
                    ("Skandia",100)
        """
    )
    db.commit()
    response.status = 200

@get('/movies')
def get_movies():
    c = db.cursor()
    c.execute(
        """
        SELECT   imdb_key, movie_name, production_year
        FROM     movies
        """
    )
    found = [{"imdbKey": imdb_key,"title": movie_name, "year": production_year}
             for imdb_key,movie_name, production_year in c]
    response.status = 200
    return {"data": found}

@get('/theaters')
def get_theaters():
    c = db.cursor()
    c.execute(
        """
        SELECT   theater_name, capacity
        FROM     theaters
        """
    )
    found = [{"name": theater_name,"capacity": capacity}
             for theater_name,capacity in c]
    response.status = 200
    return {"data": found}

run(host = 'localhost', port = PORT)