from bottle import get, post, run, request, response, delete
from urllib.parse import quote, unquote
import sqlite3


db = sqlite3.connect("krusty-db.sqlite")
db.execute("PRAGMA foreign_keys = ON")
PORT = 8888
INGREDIENTS_FOR_PALLET = 54


@post('/reset')
def post_reset():
    c = db.cursor()
    c.executescript(
        """
        DELETE FROM customers;
        DELETE FROM cookies;
        DELETE FROM recipes;
        DELETE FROM ingredients;
        DELETE FROM pallets;
        DELETE FROM requests;
        DELETE FROM requestedCookies;
        """
    )
    db.commit()
    response.status = 205
    return {"location": "/"}


@post('/customers')
def post_customers():
    customer = request.json
    c = db.cursor()
    c.execute(
        """
        INSERT
        INTO Customers(customer_name, address)
        VALUES (?, ?)
        """,
        [customer['name'], customer['address']]
    )
    response.status = 201
    db.commit()
    return {"location": "/customers/" + quote(customer['name'])}


@post('/ingredients')
def post_ingredients():
    ingredients = request.json
    c = db.cursor()
    c.execute(
            """
            INSERT
            INTO       ingredients(ingredient_name, unit, stored_ingredient_amount)
            VALUES     (?, ?, 0)
            """,
        [ingredients['ingredient'], ingredients['unit']]
    )
    db.commit()
    response.status = 201
    return {"location": "/ingredients/" + quote(ingredients['ingredient'])}


@post('/ingredients/<ingredient_name>/deliveries')
def post_ingredients(ingredient_name):
    ingredients = request.json
    c = db.cursor()
    c.execute(
        """
        UPDATE ingredients
        SET last_delivery_date = ?,
            last_delivery_amount = ?,
            stored_ingredient_amount = stored_ingredient_amount + ? 
        WHERE ingredient_name LIKE ?  
        """,
        [ingredients['deliveryTime'], ingredients['quantity'],
         ingredients['quantity'], ingredient_name]
    )
    db.commit()
    c.execute(
        """
        SELECT ingredient_name, stored_ingredient_amount, unit
        FROM ingredients
        """
    )
    response.status = 201
    found = [{"ingredient": ingredient_name, "quantity": stored_ingredient_amount, "unit": unit}
             for ingredient_name, stored_ingredient_amount, unit in c]
    return {"data": found}


@post('/cookies')
def post_cookies():
    cookie = request.json
    recipe = [(cookie["name"], x["ingredient"], x["amount"]) for x in cookie["recipe"]]
    c = db.cursor()
    c.execute(
        """
        INSERT
        INTO cookies(cookie_name)
        VALUES (?)
        """,
        [cookie['name']]
    )
    db.commit()
    c.executemany(
        """
        INSERT
        INTO recipes(cookie_name, ingredient_name, ingredient_amount)
        VALUES (?,?,?);
        """,
        recipe
    )
    response.status = 201
    db.commit()
    return {"location": "/cookies/" + quote(cookie['name'])}


@post('/cookies/<cookie_name>/block')
def block_cookies(cookie_name):
    query = """
    UPDATE pallets
    SET blocked = 1
    WHERE cookie_name = ?
    """
    params = [cookie_name]
    if request.query.after:
        query += "AND date(production_date) > ?"
        params.append(unquote(request.query.after))
    if request.query.before:
        query += "AND date(production_date) < ?"
        params.append(unquote(request.query.before))
    c = db.cursor()
    c.execute(query, params)
    db.commit()
    response.status = 205
    return {""}


@post('/cookies/<cookie_name>/unblock')
def unblock_cookies(cookie_name):
    c = db.cursor()
    query = """
    UPDATE pallets
    SET blocked = false
    WHERE cookie_name IS ?
    """
    params = [cookie_name]
    if request.query.after:
        query += "AND date(production_date) > ?"
        params.append(request.query.after)
    if request.query.before:
        query += "AND date(production_date) < ?"
        params.append(request.query.before)
    c.execute(query, params)
    db.commit()
    response.status = 205
    return {""}
    

@post('/pallets')
def post_pallets():
    pallet = request.json
    c = db.cursor()
    c.execute(
        """
        SELECT   1
        FROM     recipes
        JOIN     ingredients USING (ingredient_name)
        WHERE    stored_ingredient_amount < (ingredient_amount * ?) 
        AND      cookie_name = ? 
        """,
        [INGREDIENTS_FOR_PALLET, pallet['cookie']]
    )
    lacking_ingredients = c.fetchone()
    if lacking_ingredients:
        response.status = 422
        return "Not enough ingredients in storage"
    c.execute(
        """
        INSERT
        INTO pallets(cookie_name, production_date, blocked)
        VALUES (?, DATETIME("NOW"), false)
        """,
        [pallet['cookie']]
    )
    db.commit()
    c.execute(
        """
        UPDATE ingredients
        SET stored_ingredient_amount = stored_ingredient_amount - (
        SELECT ingredient_amount * ?
        FROM recipes
        WHERE recipes.ingredient_name = ingredients.ingredient_name AND
                recipes.cookie_name = ?
        )
        WHERE ingredient_name IN (
        SELECT ingredient_name
        FROM recipes
        WHERE cookie_name = ?
        )
        """,
        [INGREDIENTS_FOR_PALLET, pallet['cookie'], pallet['cookie']]
    )
    db.commit()
    c.execute(
        """
        SELECT pallet_id
        FROM pallets
        WHERE rowid = last_insert_rowid()
        """
    )
    response.status = 201
    id, = c.fetchone()
    return {"location": "/pallets/" + id}


@get('/ingredients')
def get_ingredients():
    c = db.cursor()
    c.execute(
        """
        SELECT ingredient_name, stored_ingredient_amount, unit
        FROM ingredients
        """
    )
    db.commit()
    response.status = 200
    found = [{"ingredient": ingredient_name, "quantity": stored_ingredient_amount,
              "unit": unit} for ingredient_name, stored_ingredient_amount, unit in c]
    return {"data": found}


@get('/cookies')
def get_cookies():
    c = db.cursor()
    c.execute(
        """
        SELECT cookie_name, count(blocked) as approved_pallets
        FROM cookies
        JOIN pallets
        USING (cookie_name)
        WHERE NOT blocked 
        GROUP BY cookie_name
        """
    )
    found = [{"name": cookie_name, "pallets": approved_pallets} for cookie_name, approved_pallets in c]
    if not found:
        c.execute(
            """
            SELECT cookie_name
            FROM cookies
            """
        )
        found = [{"name": cookie_name[0]} for cookie_name in c]
    response.status = 200
    return {"data": found}
   


@get('/cookies/<cookie_name>/recipe')
def get_cookie(cookie_name):
    c = db.cursor()
    c.execute(
        """
    SELECT   ingredient_name, ingredient_amount, unit
    FROM     recipes
    JOIN     ingredients USING (ingredient_name)
    WHERE    cookie_name = ?
    """,
        [cookie_name]
    )
    found = [{"ingredient": ingredient_name, "amount": ingredient_amount, "unit": unit}
             for ingredient_name, ingredient_amount, unit in c]
    if found:
        response.status = 200
        return {"data": found}
    else:
        response.status = 200
        return {"data": []}


@get('/pallets')
def get_pallets():
    try:
        query = """
        SELECT  pallet_id, cookie_name, production_date, blocked
        FROM    pallets
        WHERE 1 = 1
        """
        params = []
        if request.query.cookie:
            query += "AND cookie_name = ?"
            params.append(unquote(request.query.cookie))
        if request.query.after:
            query += "AND date(production_date) > ?"
            params.append(unquote(request.query.after))
        if request.query.before:
            query += "AND date(production_date) < ?"
            params.append(unquote(request.query.before))
        c = db.cursor()
        if(params):
            c.execute(query, params)
        else:
            c.execute(query)
        found = [{"id": pallet_id, "cookie": cookie_name, "productionDate": pallet_time.split()[0], "blocked": blocked} for pallet_id, cookie_name, pallet_time, blocked in c]
        if found:
            response.status = 200
        else:
            response.status = 404
        return {"data": found}
    except:
        response.status = 404
        return {"data": []}


run(host='localhost', port=PORT)


