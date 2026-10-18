import sqlite3
import pytest

from src.database.config_database import connect, create_tables


def test_order_rejects_nonexistent_customer(tmp_path):
    db_path = tmp_path / "test.db"

    connection = connect(str(db_path))
    create_tables(connection)

    try:
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                """
                INSERT INTO orders (
                    order_id,
                    customer_id,
                    discount,
                    status,
                    created_date
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    "order-test-1",
                    "customer-does-not-exist",
                    "0",
                    "PENDING",
                    "2026-10-18",
                ),
            )
    finally:
        connection.close()
        
        

def test_order_item_rejects_nonexistent_product(tmp_path):
    db_path = tmp_path / "test_items.db"

    connection = connect(str(db_path))
    create_tables(connection)

    try:
        # أولًا: نضيف عميلًا صالحًا
        connection.execute(
            """
            INSERT INTO customers
                (customer_id, name, email, phone, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("customer-1", "Test Customer", "test@example.com",
             "0500000000", "ACTIVE"),
        )

        # ثانيًا: نضيف طلبًا صالحًا لهذا العميل
        connection.execute(
            """
            INSERT INTO orders
                (order_id, customer_id, discount, status, created_date)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("order-1", "customer-1", "0", "PENDING", "2026-10-18"),
        )

        # ثالثًا: نحاول إضافة عنصر لمنتج غير موجود
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                """
                INSERT INTO order_items
                    (order_item_id, order_id, product_id,
                     quantity, unit_price)
                VALUES (?, ?, ?, ?, ?)
                """,
                ("item-1", "order-1", "missing-product", 1, "10.00"),
            )
    finally:
        connection.close()



def test_payment_rejects_nonexistent_order(tmp_path):
    db_path = tmp_path / "test_payments.db"

    connection = connect(str(db_path))
    create_tables(connection)

    try:
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                """
                INSERT INTO payments (
                    payment_id,
                    order_id,
                    amount,
                    method,
                    status
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    "payment-1",
                    "missing-order",
                    "100.00",
                    "CARD",
                    "PENDING",
                ),
            )
    finally:
        connection.close()




@pytest.mark.parametrize("quantity", [0, -1, -10])
def test_order_item_rejects_nonpositive_quantity(tmp_path, quantity):
    db_path = tmp_path / "test_quantity.db"

    connection = connect(str(db_path))
    create_tables(connection)

    try:
        connection.execute(
            """
            INSERT INTO customers
                (customer_id, name, email, phone, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("customer-1", "Test Customer", "test@example.com",
             "0500000000", "ACTIVE"),
        )

        connection.execute(
            """
            INSERT INTO products
                (product_id, name, description, price, stock, category, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            ("product-1", "Test Product", "Test", "10.00",
             10, "OTHER", "ACTIVE"),
        )

        connection.execute(
            """
            INSERT INTO orders
                (order_id, customer_id, discount, status, created_date)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("order-1", "customer-1", "0", "PENDING", "2026-10-18"),
        )

        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                """
                INSERT INTO order_items
                    (order_item_id, order_id, product_id,
                     quantity, unit_price)
                VALUES (?, ?, ?, ?, ?)
                """,
                ("item-1", "order-1", "product-1", quantity, "10.00"),
            )
    finally:
        connection.close()




def test_order_item_accepts_positive_quantity(tmp_path):
    connection = connect(str(tmp_path / "test_valid_quantity.db"))
    create_tables(connection)

    try:
        connection.execute(
            """
            INSERT INTO customers
                (customer_id, name, email, phone, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("customer-1", "Test Customer", "test@example.com",
             "0500000000", "ACTIVE"),
        )

        connection.execute(
            """
            INSERT INTO products
                (product_id, name, description, price, stock, category, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            ("product-1", "Test Product", "Test", "10.00",
             10, "OTHER", "ACTIVE"),
        )

        connection.execute(
            """
            INSERT INTO orders
                (order_id, customer_id, discount, status, created_date)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("order-1", "customer-1", "0", "PENDING", "2026-10-18"),
        )

        connection.execute(
            """
            INSERT INTO order_items
                (order_item_id, order_id, product_id, quantity, unit_price)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("item-1", "order-1", "product-1", 2, "10.00"),
        )

        result = connection.execute(
            "SELECT quantity FROM order_items WHERE order_item_id = ?",
            ("item-1",),
        ).fetchone()

        assert result == (2,)
    finally:
        connection.close()






def test_customer_rejects_duplicate_email(tmp_path):
    connection = connect(str(tmp_path / "test_unique_email.db"))
    create_tables(connection)

    try:
        connection.execute(
            """
            INSERT INTO customers
                (customer_id, name, email, phone, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("customer-1", "Customer One", "same@example.com",
             "0500000001", "ACTIVE"),
        )

        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                """
                INSERT INTO customers
                    (customer_id, name, email, phone, status)
                VALUES (?, ?, ?, ?, ?)
                """,
                ("customer-2", "Customer Two", "same@example.com",
                 "0500000002", "ACTIVE"),
            )
    finally:
        connection.close()



def test_customer_rejects_null_name(tmp_path):
    connection = connect(str(tmp_path / "test_not_null.db"))
    create_tables(connection)

    try:
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(
                """
                INSERT INTO customers
                    (customer_id, name, email, phone, status)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    "customer-1",
                    None,
                    "test@example.com",
                    "0500000000",
                    "ACTIVE",
                ),
            )
    finally:
        connection.close()
