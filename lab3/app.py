from bottle import get, post, run, request, response, delete
import sqlite3


db = sqlite3.connect("lab3/movies.sqlite")
db.execute("PRAGMA foreign_keys = ON")
PORT=7007

@get('/ping')
def get_ping():
    response.status = 200
    return 'pong'

@post('/reset')
def post_reset():
    c = db.cursor()
    c.executescript(
        """
        DELETE FROM customers;
        DELETE FROM theaters;
        DELETE FROM movies;

        INSERT
        INTO        theaters(theater_name, capacity)
        VALUES      ('Kino',10),
                    ('Regal',16),
                    ('Skandia',100)
        """
    )
    db.commit()
    response.status = 200

@post('/users')
def post_users():
    user = request.json
    c = db.cursor()
    try:
        c.execute(
            """
            INSERT
            INTO       customers(username, full_name, password)
            VALUES     (?, ?, ?)
            RETURNING  username
            """,
            [user['username'], user['fullName'], hash(user['pwd'])]
        )
    except:
        response.status = 400
        return ""
    found = c.fetchone()
    if not found:
        response.status = 400
        return "Illegal..."
    else:
        db.commit()
        response.status = 201
        username, = found
        return f"/users/{username}"

@post('/movies')
def post_movies():
    movie = request.json
    c = db.cursor()
    try:
        c.execute(
            """
            INSERT
            INTO       movies(imdb_key, movie_name, production_year)
            VALUES     (?, ?, ?)
            RETURNING  imdb_key
            """,
            [movie['imdbKey'], movie['title'], movie['year']]
        )
    except:
        response.status = 400
        return ""
    found = c.fetchone()
    if not found:
        response.status = 400
        return "Illegal..."
    else:
        db.commit()
        response.status = 201
        key, = found
        return f"/movies/{key}"

@post('/performances')
def post_performances():
    performance = request.json
    c = db.cursor()
    try:
        c.execute(
            """
            INSERT
            INTO       performances(imdb_key, theater_name, performance_date, start_time)
            VALUES     (?, ?, ?, ?)
            RETURNING  performance_id
            """,
            [performance['imdbKey'], performance['theater'], performance['date'], performance['time']]
        )
    except:
        response.status = 400
        return "No such movie or theater"
    found = c.fetchone()
    if not found:
        response.status = 400
        return "Illegal..."
    else:
        db.commit()
        response.status = 201
        id, = found
        return f"/performances/{id}"

@post('/tickets')
def post_tickets():
    ticket = request.json
    c = db.cursor() 
    c.execute(
        """
        WITH sales(performance_id, sold_tickets) AS (
            SELECT performance_id, count()
            FROM tickets
            GROUP BY performance_id
        )
        SELECT  capacity - coalesce(sold_tickets, 0)
        FROM    performances
        JOIN    theaters
        USING   (theater_name)
        LEFT OUTER JOIN sales
        USING   (performance_id)
        WHERE   performance_id = ?
        """,
        [ticket['performanceId']]
        )
    remaining_seats, = c.fetchone()
    print(remaining_seats)
    if remaining_seats < 1:
        response.status = 400
        return 'No tickets left'

    c.execute(
        """
        SELECT   1
        FROM     customers
        WHERE    username = ? AND password = ?
        """,
        [ticket['username'], hash(ticket[('pwd')])]
    )
    match = c.fetchone()
    if match != (1,):
        response.status = 401
        return "Wrong user credentials"
    try:
        c.execute(
            """
            INSERT
            INTO       tickets(username, performance_id)
            VALUES     (?, ?)
            RETURNING  ticket_id
            """,
            [ticket['username'], ticket['performanceId']]
        )
    except:
        response.status = 400
        return "ERROR"
    found = c.fetchone()
    if not found:
        response.status = 400
        return "Illegal..."
    else:
        db.commit()
        response.status = 201
        id, = found
        return f"/tickets/{id}"
    
    
    
@get('/movies')
def get_movies():
    query = """
        SELECT   imdb_key, movie_name, production_year
        FROM     movies
        WHERE    1 = 1
        """
    params = []
    if request.query.title:
        query += " AND movie_name = ?"
        params.append(unquote(request.query.title))
    if request.query.year:
        query += " AND production_year = ?"
        params.append(request.query.year)
    c = db.cursor()
    c.execute(query, params)
    found = [{"imdbKey": imdb_key,"title": movie_name, "year": production_year}
             for imdb_key,movie_name, production_year in c]
    response.status = 200
    return {"data": found}

@get('/movies/<imdb_key>')
def get_student(imdb_key):
    c = db.cursor()
    c.execute(
        """
        SELECT   imdb_key, movie_name, production_year
        FROM     movies
        WHERE    imdb_key = ?
        """,
        [imdb_key]
    )
    found = [{"imdbKey": imdb_key,"title": movie_name, "year": production_year}
             for imdb_key,movie_name, production_year in c]
    response.status = 200
    return {"data": found}

@get('/performances')
def get_performances():
    c = db.cursor()
    c.execute(
        """
        WITH sales(performance_id, sold_tickets) AS (
            SELECT performance_id, count()
            FROM tickets
            GROUP BY performance_id
            )
        SELECT  performance_id, performance_date, start_time, movie_name, production_year, theater_name, capacity - coalesce(sold_tickets, 0)
        FROM    performances
        JOIN    movies
        using   (imdb_key)
        JOIN    theaters
        USING   (theater_name)
        LEFT OUTER JOIN sales
        USING   (performance_id)
        """
            )
    found = [{"performanceId": performance_id, "date": performance_date, "startTime": start_time, "title": movie_name, "year": production_year, "theater": theater_name, "remainingSeats": remaining_seats}
             for performance_id, performance_date, start_time, movie_name, production_year, theater_name, remaining_seats in c]
    response.status = 200
    return {"data": found}

@get('/users/<username>/tickets')
def get_student_applications(username):
    c = db.cursor()
    c.execute(
        """
        
        SELECT  performance_date, start_time, theater_name, movie_name, production_year, count() AS nbr_of_tickets
        FROM    tickets
        JOIN    performances
        USING   (performance_id)
        JOIN    customers
        USING   (username)
        JOIN    movies
        USING   (imdb_key)
        WHERE   username = ?
        GROUP BY performance_id
        """,
        [username]
    )
    found = [{"date": performance_date, "startTime": start_time, "theater": theater_name, "title": movie_name, "year": production_year, "numberOfTickets": nbr_of_tickets}
             for performance_date, start_time, theater_name, movie_name, production_year, nbr_of_tickets in c]
    response.status = 200
    return {"data": found}

run(host = 'localhost', port = PORT)