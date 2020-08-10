import os
import shutil
import zipfile
from urllib import request

from mysql_connector import MySqlConnector


class HamData:
	_FULL_URL = "ftp://wirelessftp.fcc.gov/pub/uls/complete/l_amat.zip"
	_DAY_TEMPLATE_URL = "ftp://wirelessftp.fcc.gov/pub/uls/daily/l_ac_{day}.zip"
	_FILE_DIR = 'download'
	_db = None

	def __init__(self):
		mysql_connector = MySqlConnector('127.0.0.1', 'fcc_amateur', 'root', 'a')
		self._db = mysql_connector
		return

	def download_and_extract_day(self, day):
		day_url_path = self._DAY_TEMPLATE_URL.format(day=day)
		download_path = f'{self._FILE_DIR}/l_ac_{day}.zip'

		print(f"Downloading from {day_url_path}")
		data_file = request.urlopen(day_url_path)

		print(f"Writing to {download_path}")
		local_file = open(download_path, 'wb')
		shutil.copyfileobj(data_file, local_file)

		print(f"Unzipping to {self._FILE_DIR}")
		zip_ref = zipfile.ZipFile(download_path, 'r')
		zip_ref.extractall(self._FILE_DIR)

		print(f"Removing download temp file: {download_path}")
		os.remove(download_path)

	def import_data(self):
		# "Unzipping database file EN.dat..."
		# "Unzipping database file AM.dat..."
		# "Unzipping database file HD.dat..."
		print("Starting entities table...")

		self._db.execute_query("""CREATE TABLE IF NOT EXISTS en_entities
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
								index call_sign_idx(call_sign));""")

		en_file = open(f"{self._FILE_DIR}/EN.dat")
		line = [None, None]

		while True:
			line_string = en_file.readline().replace('\n','')
			print(line_string)
			line = line_string.split('|')

			if len(line) <= 1:
				break

			self._db.execute_query(f"""INSERT INTO en_entities (
									fcc_id,
									call_sign,
									entity_type,
									licensee_id,
									entity_name,
									first_name,
									middle_initial,
									last_name,
									name_suffix,
									phone,
									email,
									street_address,
									city,
									state,
									zip,
									po_box,
									address_attn_line,
									fcc_reg_number)
									VALUES ('{line[1]}', '{line[4]}', '{line[5]}', '{line[6]}', '{line[7]}', '{line[8]}', '{line[9]}',
										'{line[10]}', '{line[11]}', '{line[12]}', '{line[14]}', '{line[15]}', '{line[16]}', '{line[17]}',
										'{line[18]}', '{line[19]}', '{line[20]}', '{line[22]}')
									""")
