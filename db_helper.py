import sqlite3


class DbHelper:
    def __init__(self, file: str):
        self.db = sqlite3.connect(file)

    def create(self, table: str, cols: list):
        cur = self.db.cursor()
        cols = ', '.join(cols)
        cur.execute(f'CREATE TABLE IF NOT EXISTS {table}({cols})')
        cur.close()
        self.db.commit()

    def select(self, table: str, value='*'):
        cur = self.db.cursor()
        values = cur.execute(f'SELECT {value} from {table}').fetchall()
        cur.close()
        return values

    def select_where(self, table: str, condition: str, value='*'):
        cur = self.db.cursor()
        values = cur.execute(f'SELECT {value} FROM {table} WHERE {condition}').fetchall()
        cur.close()
        return values

    def insert(self, table: str, cols: list, values: list):
        cols = ','.join(cols)
        values = ','.join(values)
        cur = self.db.cursor()
        cur.execute(f'INSERT INTO {table}({cols}) VALUES({values})')
        cur.close()
        self.db.commit()

    def update(self, table: str, col_and_value: str):
        cur = self.db.cursor()
        cur.execute(f'UPDATE {table} SET {col_and_value}')
        self.db.commit()
        cur.close()

    def update_where(self, table: str, col_and_value: str, condition: str):
        cur = self.db.cursor()
        cur.execute(f'UPDATE {table} SET {col_and_value} WHERE {condition}')

    def delete_where(self, table: str, condtion: str):
        cur = self.db.cursor()
        cur.execute(f'DELETE FROM {table} WHERE {condtion}')
        self.db.commit()
        cur.close()