import mysql.connector


class MySqlConnector:
	_cursor = None
	_connection = None

	def __init__(self, host, database, user, password):
		self._connection = mysql.connector.connect(host=host,
												user=user,
												password=password)

		self._cursor = self._connection.cursor()
		self._cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
		self._cursor.execute(f"USE {database}")
		return

	def execute_query(self, query):
		self._cursor.execute(query)
		self._connection.commit()
		print(self._cursor.rowcount)
		return

