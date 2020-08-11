import logging

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

		self.execute_query("""CREATE TABLE IF NOT EXISTS en_entities
								(fcc_id int not null,
								call_sign varchar(10),
								entity_type varchar(2),
								licensee_id varchar(9),
								entity_name varchar(200),
								first_name varchar(20),
								middle_initial varchar(1),
								last_name varchar(20),
								name_suffix varchar(3),
								phone varchar(10),
								email varchar(50),
								street_address varchar(60),
								city varchar(20),
								state varchar(2),
								zip varchar(9),
								po_box varchar(20),
								address_attn_line varchar(35),
								fcc_reg_number varchar(10),
								primary key(fcc_id),
								index fcc_id_idx(fcc_id),
								index call_sign_idx(call_sign))""")

		self.execute_query("""CREATE TABLE IF NOT EXISTS am_amateur
								(fcc_id int not null,
								call_sign varchar(10),
								operator_class varchar(1),
								index fcc_id_idx(fcc_id),
								index call_sign_idx(call_sign))""")

		self.execute_query("""CREATE TABLE IF NOT EXISTS hd_license_header
								(fcc_id int not null,
								call_sign varchar(10),
								license_status varchar(1),
								grant_date date,
								expired_date date,
								cancellation_date date,
								reserved varchar(1),
								index fcc_id_idx(fcc_id),
								index call_sign_idx(call_sign))""")
		return

	def execute_query(self, query, commit=True):
		try:
			self._cursor.execute(query)
			if commit:
				self._connection.commit()
		except Exception as ex:
			logging.error(f"Error running query: ```{query}```")
			raise ex
		return

	def fetchone(self):
		return self._cursor.fetchone()

	def commit(self):
		self._connection.commit()

	def __del__(self):
		self._connection.disconnect()
