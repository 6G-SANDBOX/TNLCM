import os

from mysql.connector import connect

class MysqlHandler:

    def __init__(self):
        self.connection = connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DATABASE'),
            port=os.getenv('MYSQL_PORT')
        )
        self.cursor = self.connection.cursor()
    
    def execute_query(self, query, params=None):
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        return self.cursor.fetchall()

    def commit(self):
        self.connection.commit()
    
    def close(self):
        self.cursor.close()
        self.connection.close()