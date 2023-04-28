-- Populates the tables with data.
-- We will do a lot of inserts, so we start a transaction to make it faster.
-- Table data was generated using chatGPT

BEGIN TRANSACTION;

-- Populate the customer table.

INSERT OR REPLACE
INTO   customers(customer_name, address)
VALUES  ('Bullar och bong', 'Bakgatan 4, Lund'),
        ('Café Ingalunda', 'ÅtervÄndsgränden 1, Kivik'),
        ('Kakbak HB', 'Degkroken 8, Malmö');

-- Populate the cookie table.

INSERT OR REPLACE
INTO       cookies(cookie_name)
VALUES  ('Tango'),
        ('Almond delight');
-- Populate the ingredient table.

INSERT OR REPLACE
INTO   ingredients(ingredient_name, stored_ingredient_amount,unit)
VALUES  ('Flour', 500000, 'g'),
        ('Butter', 200000, 'g'),
        ('Icing sugar', 100000, 'g'),
        ('Roasted chopped nuts', 200000, 'g'),
        ('Fine-ground nuts', 200000, 'g'),
        ('Ground roasted nuts', 200000, 'g'),
        ('Bread crumbs', 150000, 'g'),
        ('Sugar', 500000, 'g'),
        ('Egg whites', 350000, 'g'),
        ('Chocolate', 300000, 'g'),
        ('Marzipan', 100000, 'g'),
        ('Eggs', 300000, 'g'),
        ('Potato starch', 100000, 'g'),
        ('Wheat flour', 600000, 'g'),
        ('Sodium bicarbonate', 25000, 'g'),
        ('Vanilla', 100000, 'g'),
        ('Chopped almonds', 250000, 'g'),
        ('Cinnamon', 40000, 'g'),
        ('Vanilla sugar', 40000, 'g');

-- Commit the transaction.

END TRANSACTION;

--Powershell promt, enter in terminal:
--cd Documents\Programming\edaf75-project-group-53
--Get-Content initial-data.sql | & sqlite3 krusty-db.sqlite

