from decimal import Decimal
import decimal
from shlex import join
import sqlite3
from tracemalloc import start


def connect():
    connection = sqlite3.connect(r"data.db")
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


connection = connect()


cursor = connection.cursor()
queries = {
    # ------------------------------------------------------------------------------------------- #
    "create_customer": """create table if not exists customers(id integer PRIMARY KEY,
     name varchar,
     email varchar,
     phone varchar,
     status varchar)
    """,
    # ------------------------------------------------------------------------------------------- #
    "create_product": """create table if not exists products(id integer PRIMARY KEY,
    name varchar,
    description text,
    price varchar,
    stock integer,
    category varchar,
    status varchar)
    """,
    # ------------------------------------------------------------------------------------------- #
    "create_order": "create table if not exists orders(id integer PRIMARY KEY, customer_id integer NOT NULL, discount varchar, status varchar, created_date text, FOREIGN KEY(customer_id) references customers(id))",
    # ------------------------------------------------------------------------------------------- #
    "create_items": """create table if not exists order_items(id integer PRIMARY KEY, 
    order_id integer NOT NULL,
    product_id integer NOT NULL,
    quantity integer NOT NULL CHECK(quantity > 0),
    unit_price varchar NOT NULL,
    FOREIGN KEY(order_id) references orders(id),FOREIGN KEY(product_id) REFERENCES products(id) )
    """,
}

for query in queries.keys():
    cursor.execute(queries[query])


def add_customer(
    customer_name: str, customer_email: str, customer_phone: str, customer_status: str
):

    add_customer_query = (
        """insert into customers (name,email,phone,status) values (?,?,?,?)"""
    )
    cursor.execute(
        add_customer_query,
        (customer_name, customer_email, customer_phone, customer_status),
    )

    connection.commit()


def add_product(
    product_name: str,
    product_desc: str,
    product_price: str,
    product_stock: int,
    product_category: str,
    product_status: str,
):

    add_product_query = """insert into products (name,description,price,stock,category,status) values (?,?,?,?,?,?)"""
    cursor.execute(
        add_product_query,
        (
            product_name,
            product_desc,
            product_price,
            product_stock,
            product_category,
            product_status,
        ),
    )

    connection.commit()


def add_order(customer_id: int, discount: str, status: str, created_date: str):

    add_order_query = """insert into orders (customer_id,discount,status,created_date) values (?,?,?,?)"""
    cursor.execute(add_order_query, (customer_id, discount, status, created_date))

    connection.commit()


def add_order_item(order_id: int, product_id: int, quantity: int, unit_price: str):

    add_order_query = """insert into order_items (order_id,product_id,quantity,unit_price) values (?,?,?,?)"""
    cursor.execute(add_order_query, (order_id, product_id, quantity, unit_price))

    connection.commit()


def get_customers() -> list[tuple]:
    connection = connect()
    cursor = connection.cursor()

    query = "select (name) from customers"
    cursor.execute(query)

    data = cursor.fetchall()
    connection.close()
    return data


def get_customer_by_id(id: int) -> tuple | None:
    connection = connect()
    cursor = connection.cursor()

    query = "select* from customers where id=?"
    cursor.execute(query, (id,))

    data = cursor.fetchone()
    connection.close()
    return data


def update_customer_by_id(id: int, column_name: str, new_value: str) -> None:
    allowed_columns = {"name", "email", "phone", "status"}
    if column_name in allowed_columns:

        connection = connect()
        cursor = connection.cursor()

        query = f"update customers set {column_name} = (?) where id=(?)"
        cursor.execute(query, (new_value, id))
        connection.commit()
        connection.close()
    else:
        raise ValueError("Please insert a valid column name")


def delete_customer_by_id(customer_id: int) -> None:
    connection = connect()
    cursor = connection.cursor()
    try:

        query = "delete from customers where id=(?)"
        cursor.execute(query, (customer_id,))
        connection.commit()
    except sqlite3.IntegrityError:
        print("Please check your constraint relations before deleting... ")
    connection.close()


def join_together() -> list | None:
    connection = connect()
    cursor = connection.cursor()
    query = "select name, orders.discount, orders.status, orders.created_date from customers  join orders on customers.id = orders.customer_id"
    cursor.execute(query)
    data = cursor.fetchall()
    connection.close()
    return data


def left_join_together() -> list | None:
    connection = connect()
    cursor = connection.cursor()
    query = "select name, orders.discount, orders.status, orders.created_date from customers left join orders on customers.id = orders.customer_id"
    cursor.execute(query)
    data = cursor.fetchall()
    connection.close()
    return data


def right_join_together() -> list | None:
    connection = connect()
    cursor = connection.cursor()
    query = "select name, orders.discount, orders.status, orders.created_date from customers right join orders on customers.id = orders.customer_id"
    cursor.execute(query)
    data = cursor.fetchall()
    connection.close()
    return data


def inner_join_together() -> list | None:
    connection = connect()
    cursor = connection.cursor()
    query = "select name, orders.discount, orders.status, orders.created_date from customers inner join orders on customers.id = orders.customer_id"
    cursor.execute(query)
    data = cursor.fetchall()
    connection.close()
    return data


customers = [
    ("basheer", "basheerFadi@gmail.com", "01015803348", "active"),
    ("osama", "osama@gmail.com", "0505172741", "active"),
    ("mazen", "mazen@gmail.com", "0505172741", "in active"),
    ("noor", "noor@gmail.com", "960218716", "in active"),
]


products = [
    ("mouse", "mouse wireless", "2100.00", 120, "Computer", "active"),
    ("keyboard", "keyboard wireless", "3000.00", 50, "Computer", "active"),
    ("touch pad", "touch pad", "500", 15, "accessories", "active"),
    ("ps5", "ps5", "4000", 20, "entertainment", "active"),
]


def add_seven_orders():
    add_order(1, "20", "pending", "08/10/2026")
    add_order(1, "30", "success", "08/10/2026")
    add_order(2, "50", "denied", "08/10/2026")
    add_order(2, "100", "pending", "08/10/2026")
    add_order(2, "120", "denied", "08/10/2026")
    add_order(3, "90", "success", "08/10/2026")
    add_order(3, "30", "denied", "08/10/2026")


def add_seven_order_items():
    add_order_item(1, 1, 5, "2100")
    add_order_item(2, 2, 4, "1100")
    add_order_item(3, 3, 3, "2500")
    add_order_item(3, 3, 2, "6000")
    add_order_item(3, 3, 7, "4000")
    add_order_item(4, 4, 15, "2300")
    add_order_item(2, 2, 9, "2200")


# for customer in customers:
#     add_customer(*customer)

# for product in products:
#     add_product(*product)

# add_seven_orders()
# add_seven_order_items()


def multi_join_together() -> list | None:
    connection = connect()
    cursor = connection.cursor()
    query = "select CUS.name, ORD.id,PRO.name,ORD_ITM.quantity, ORD_ITM.unit_price from customers CUS join orders ORD on CUS.id = ORD.customer_id join order_items ORD_ITM on ORD_ITM.order_id = ORD.id join products PRO on PRO.id = ORD_ITM.product_id"
    cursor.execute(query)
    data = cursor.fetchall()
    connection.close()
    return data


data = multi_join_together()
new_data = []
if data is not None:
    for i in data:
        name = i[0]
        order_id = i[1]
        item = i[2]
        quantity = i[3]
        unit_price = Decimal(i[4]).quantize(Decimal("0.00"), decimal.ROUND_HALF_UP)
        new_data.append(
            {
                "name": name,
                "order_id": order_id,
                "item": item,
                "quantity": quantity,
                "unit_price": unit_price,
            }
        )


for item in new_data:
    print(
        f"{item['name']} purchased {item['item']} -> qty:{item['quantity']} / price is :{item["unit_price"]} ||| with total amount : {item['unit_price'] *item['quantity'] }"
    )
    print("--"*20)


connection.commit()

connection.close()
