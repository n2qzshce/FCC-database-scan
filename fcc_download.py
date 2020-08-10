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
		url_path = self._DAY_TEMPLATE_URL.format(day=day)
		download_path = f'{self._FILE_DIR}/l_ac_{day}.zip'
		self._download_and_extract(url_path, download_path)

	def download_and_extract_week(self):
		url_path = self._FULL_URL
		download_path = f'{self._FILE_DIR}/l_amat.zip'
		self._download_and_extract(url_path, download_path)

	def cleanup_downloads(self):
		for filename in os.listdir(f'{self._FILE_DIR}'):
			file_path = os.path.join(f'{self._FILE_DIR}', filename)
			os.unlink(file_path)

	def _download_and_extract(self, url_path, download_path):
		data_file = request.urlopen(url_path)

		local_file = open(download_path, 'wb')
		shutil.copyfileobj(data_file, local_file)

		try:
			zip_ref = zipfile.ZipFile(download_path, 'r')
			zip_ref.extractall(self._FILE_DIR)
		except zipfile.BadZipFile:
			del zip_ref
		finally:
			del zip_ref

		os.remove(download_path)

	def import_data(self):
		self._parse_en_file()
		self._parse_am_file()
		self._parse_hd_file()

	def _parse_en_file(self):
		try:
			en_file = open(f"{self._FILE_DIR}/EN.dat")
		except FileNotFoundError:
			return

		while True:
			line_string = en_file.readline().replace('\n', '')
			line_string = line_string.replace("'", "\\'")
			line = line_string.split('|')
			print(line_string)

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
											ON DUPLICATE KEY UPDATE `fcc_id`={line[1]}
											""")
		en_file.close()

	def _parse_am_file(self):
		try:
			am_file = open(f"{self._FILE_DIR}/AM.dat")
		except FileNotFoundError:
			return
		while True:
			line_string = am_file.readline().replace('\n', '')
			line = line_string.split('|')

			if len(line) <= 1:
				break
			self._db.execute_query(f"""INSERT INTO am_amateur (
											fcc_id,
											call_sign,
											operator_class)
											VALUES('{line[1]}', '{line[4]}', '{line[5]}')
											ON DUPLICATE KEY UPDATE `fcc_id`={line[1]}
											""")
		am_file.close()

	def _parse_hd_file(self):
		try:
			hd_file = open(f"{self._FILE_DIR}/HD.dat")
		except FileNotFoundError:
			return
		while True:
			line_string = hd_file.readline().replace('\n', '')
			line = line_string.split('|')

			if len(line) <= 1:
				break

			self._db.execute_query(f"""INSERT INTO hd_license_header (
									fcc_id,
									call_sign,
									license_status,
									grant_date,
									expired_date,
									cancellation_date,
									reserved)
									VALUES('{line[1]}', '{line[4]}', '{line[5]}', {self._mysql_date_str(line[7])}, 
									{self._mysql_date_str(line[8])}, {self._mysql_date_str(line[9])}, '{line[11]}')
									ON DUPLICATE KEY UPDATE `fcc_id`={line[1]}
									""")
		hd_file.close()

	@staticmethod
	def _mysql_date_str(string_val):
		if string_val == '':
			return 'NULL'
		else:
			return f"STR_TO_DATE('{string_val}','%m/%d/%Y')"
