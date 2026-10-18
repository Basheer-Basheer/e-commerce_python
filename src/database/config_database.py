import sqlite3


def connect(path: str):
    connection = sqlite3.connect(rf"{path}")
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def create_tables(connection: sqlite3.Connection) -> None:

    queries = {
        # ------------------------------------------------------------------------------------------- #
        "create_customer": """create table if not exists customers(customer_id TEXT PRIMARY KEY,
     name varchar NOT NULL,
     email varchar NOT NULL UNIQUE,
     phone varchar NOT NULL,
     status varchar NOT NULL check(status in ('ACTIVE', 'INACTIVE', 'BLOCKED'))
    )
    """,
        # ------------------------------------------------------------------------------------------- #
        "create_product": """create table if not exists products(product_id TEXT PRIMARY KEY,
    name varchar,
    description text,
    price varchar,
    stock integer,
    category varchar,
    status varchar )
    """,
        # ------------------------------------------------------------------------------------------- #
        "create_order": "create table if not exists orders(order_id TEXT PRIMARY KEY, customer_id TEXT NOT NULL, discount varchar, status varchar, created_date text, FOREIGN KEY(customer_id) references customers(customer_id))",
        # ------------------------------------------------------------------------------------------- #
        "create_items": """create table if not exists order_items(order_item_id TEXT PRIMARY KEY, 
    order_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    quantity integer NOT NULL CHECK(quantity > 0),
    unit_price varchar NOT NULL,
    FOREIGN KEY(order_id) references orders(order_id),FOREIGN KEY(product_id) REFERENCES products(product_id) )
    """,
        "create_payment": """
    CREATE TABLE IF NOT EXISTS payments (
        payment_id TEXT PRIMARY KEY,
        order_id TEXT NOT NULL,
        amount VARCHAR NOT NULL,
        method VARCHAR NOT NULL,
        status VARCHAR NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(order_id)
    )
""",
    }

    cursor = connection.cursor()
    for query in queries.keys():
        cursor.execute(queries[query])
    connection.commit()


connection = connect("data.db")
print(connection.execute("PRAGMA foreign_keys").fetchone())
create_tables(connection=connection)

print(
    connection.execute(
        "PRAGMA table_info(order_items)"
    ).fetchall()
)