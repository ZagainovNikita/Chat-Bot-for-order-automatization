import os
import mysql.connector


class DataBase:
    def __init__(self):
        # put in here your MySQL database data
        self.host = os.getenv("DB_HOST")
        self.database = os.getenv("DB_DATABASE")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")

    @property
    def conn(self):
        return mysql.connector.connect(
            host=self.host,
            database=self.database,
            user=self.user,
            password=self.password
        )

    def execute_query(self,
                      query: str,
                      args: tuple = None,
                      fetchone: bool = False,
                      fetchall: bool = False):
        conn = self.conn
        result = None
        try:
            cur = conn.cursor()

            if args:
                cur.execute(query, args)
            else:
                cur.execute(query)

            if fetchone:
                result = cur.fetchone()
            elif fetchall:
                result = cur.fetchall()
            else:
                conn.commit()

        except:
            return None

        finally:
            conn.close()
            return result

    def get_order_status(self, order_id: int) -> tuple:
        query = "SELECT status FROM order_tracking WHERE order_id = %s"
        status = self.execute_query(query, (order_id,), fetchone=True)
        return status

    def get_menu(self) -> list:
        query = "SELECT name FROM food_items"
        menu = self.execute_query(query, fetchall=True)
        return [item[0] for item in menu]

    def get_new_order_id(self) -> int:
        query = "SELECT MAX(order_id) FROM orders"
        result = self.execute_query(query, fetchone=True)
        if not result:
            result = (0,)
        return result[0] + 1

    def add_to_orders(self, order_id: int, item: str, quantity: int):
        get_price_query = "SELECT item_id, price FROM food_items WHERE name = %s"
        item_id, price = self.execute_query(get_price_query, (item,), fetchone=True)
        insert_order_query = ("INSERT INTO orders (order_id, item_id, quantity, total_price) " +
                              "VALUES (%s, %s, %s, %s)")
        self.execute_query(insert_order_query,
                           (order_id, item_id, quantity, quantity*float(price)))

    def create_track_id(self, order_id: int) -> int:
        query = "INSERT INTO order_tracking (order_id, status) VALUES (%s, %s)"
        self.execute_query(query, (order_id, "delivering"))
        return order_id

    def get_total_price(self, order_id: int) -> float:
        query = "SELECT total_price FROM orders WHERE order_id = %s"
        result = self.execute_query(query, (order_id,), fetchall=True)
        return sum([price[0] for price in result])