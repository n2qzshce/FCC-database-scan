import logging
import os
import shutil
import zipfile
from urllib import request

from mysql_connector import MySqlConnector


class HamData:
	_FULL_LICENSE_URL = "ftp://wirelessftp.fcc.gov/pub/uls/complete/l_amat.zip"
	_FULL_APPLICATION_URL = "ftp://wirelessftp.fcc.gov/pub/uls/complete/a_amat.zip"
	_DAY_LICENSE_TEMPLATE_URL = "ftp://wirelessftp.fcc.gov/pub/uls/daily/l_ac_{day}.zip"
	_DAY_APPLICATION_TEMPLATE_URL = "ftp://wirelessftp.fcc.gov/pub/uls/daily/a_am_{day}.zip"
	_FILE_DIR = 'download'
	_db = None

	def __init__(self):
		mysql_connector = MySqlConnector('127.0.0.1', 'fcc_amateur', 'root', 'a')
		self._db = mysql_connector
		return

	def download_and_extract_day(self, day):
		logging.info(f"Downloading day: {day}")
		os.makedirs(f"{self._FILE_DIR}/license", exist_ok=True)
		os.makedirs(f"{self._FILE_DIR}/application", exist_ok=True)

		url_path = self._DAY_LICENSE_TEMPLATE_URL.format(day=day)
		download_path = f'{self._FILE_DIR}/license/l_ac_{day}.zip'
		self._download_and_extract(url_path, download_path)

		url_path = self._DAY_APPLICATION_TEMPLATE_URL.format(day=day)
		download_path = f'{self._FILE_DIR}/application/a_am_{day}.zip'
		self._download_and_extract(url_path, download_path)

	def download_and_extract_week(self):
		logging.info(f"Downloading full week")
		os.makedirs(f"{self._FILE_DIR}/license", exist_ok=True)
		os.makedirs(f"{self._FILE_DIR}/application", exist_ok=True)

		url_path = self._FULL_LICENSE_URL
		download_path = f'{self._FILE_DIR}/license'
		self._download_and_extract(url_path, download_path, "l_amat.zip")

		url_path = self._FULL_APPLICATION_URL
		download_path = f'{self._FILE_DIR}/application'
		self._download_and_extract(url_path, download_path, "a_amat.zip")

	def cleanup_downloads(self):
		for filename in os.listdir(f'{self._FILE_DIR}'):
			if filename in ['application', 'license']:
				continue
			file_path = os.path.join(f'{self._FILE_DIR}', filename)
			logging.info(f"Deleting {file_path}")
			os.unlink(file_path)

	def _download_and_extract(self, url_path, download_path, filename):
		# noinspection PyUnusedLocal
		zip_ref = None

		for x in range(1, 3):
			logging.info(f"Attempt {x} downloading {url_path}")
			data_file = request.urlopen(url_path)

			logging.info(f"Extracting {download_path}/{filename}")
			local_file = open(f"{download_path}/{filename}", 'wb')
			shutil.copyfileobj(data_file, local_file)

			try:
				zip_ref = zipfile.ZipFile(f"{download_path}/{filename}", 'r')
				zip_ref.extractall(download_path)
				break
			except zipfile.BadZipFile:
				logging.error(f"Error opening zip file: {download_path}")
			finally:
				del zip_ref

		os.remove(f"{download_path}/{filename}")

	def import_data(self):
		self._parse_en_file()
		self._parse_am_file()
		self._parse_hd_file()
		self._parse_ad_file()
		self._parse_vc_file()

	def _parse_en_file(self):
		logging.info("Parsing EN.dat")
		try:
			en_file = open(f"{self._FILE_DIR}/license/EN.dat")
		except FileNotFoundError:
			logging.error("EN.dat not found")
			return

		line_count = 0
		while True:
			line_string = en_file.readline().replace('\n', '')
			line_count += 1
			if line_count % 100 == 0:
				logging.info(f"Parsing line {line_count}")
			line_string = line_string.replace("\\", "\\\\").replace("'", "\\'")
			line = line_string.split('|')

			if len(line) <= 1:
				self._db.commit()
				break

			try:
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
												""", False)

				if line_count % 500 == 0:
					logging.info("Committing!")
					self._db.commit()
			except Exception as ex:
				logging.error(f"Error on line: ```{line_string}```", ex)
				raise ex
		en_file.close()

	def _parse_am_file(self):
		try:
			am_file = open(f"{self._FILE_DIR}/license/AM.dat")
		except FileNotFoundError:
			logging.error("AM.dat not found")
			return
		
		line_count = 0
		while True:
			line_string = am_file.readline().replace('\n', '')
			line_count += 1
			if line_count % 100 == 0:
				logging.info(f"Parsing line {line_count}")
			line = line_string.split('|')

			if len(line) <= 1:
				self._db.commit()
				break

			try:
				self._db.execute_query(f"""INSERT INTO am_amateur (
												fcc_id,
												call_sign,
												operator_class)
												VALUES('{line[1]}', '{line[4]}', '{line[5]}')
												ON DUPLICATE KEY UPDATE `fcc_id`={line[1]}
												""", False)

				if line_count % 500 == 0:
					logging.info("Committing!")
					self._db.commit()
			except Exception as ex:
				logging.error(f"Error on line: ```{line_string}```", ex)
				raise ex
		am_file.close()

	def _parse_hd_file(self):
		logging.info("Parsing HD.dat")
		try:
			hd_file = open(f"{self._FILE_DIR}/license/HD.dat")
		except FileNotFoundError:
			logging.error("HD.dat not found")
			return

		line_count = 0
		while True:
			line_string = hd_file.readline().replace('\n', '')
			line_count += 1
			if line_count % 100 == 0:
				logging.info(f"Parsing line {line_count}")
			line = line_string.split('|')

			if len(line) <= 1:
				self._db.commit()
				break

			try:
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
										""", False)

				if line_count % 500 == 0:
					logging.info("Committing!")
					self._db.commit()

			except Exception as ex:
				logging.error(f"Error on line: ```{line_string}```", ex)
				raise ex
		hd_file.close()

	def _parse_ad_file(self):
		logging.info("Parsing AD.dat")
		try:
			ad_file = open(f"{self._FILE_DIR}/application/AD.dat")
		except FileNotFoundError:
			logging.error("AD.dat not found")
			return

		line_count = 0
		while True:
			line_string = ad_file.readline().replace('\n', '')
			line_count += 1
			if line_count % 100 == 0:
				logging.info(f"Parsing line {line_count}")
			line_string = line_string.replace('\\', '')
			line = line_string.split('|')

			if len(line) <= 1:
				self._db.commit()
				break

			if line[2] != '':
				line[2] = f"'{line[2]}'"
			else:
				line[2] = 'NULL'

			try:
				self._db.execute_query(f"""INSERT INTO ad_application_detail (
										unique_identifier,
										uls_file_number,
										application_purpose,
										application_status,
										receipt_date)
										VALUES('{line[1]}', {line[2]}, '{line[4]}', '{line[6]}', 
										{self._mysql_date_str(line[10])})
										ON DUPLICATE KEY UPDATE `unique_identifier`={line[1]}
										""", False)

				if line_count % 500 == 0:
					logging.info("Committing!")
					self._db.commit()

			except Exception as ex:
				logging.error(f"Error on line: ```{line_string}```", ex)
				raise ex
		ad_file.close()

	def _parse_vc_file(self):
		logging.info("Parsing VC.dat")
		try:
			ad_file = open(f"{self._FILE_DIR}/application/VC.dat")
		except FileNotFoundError:
			logging.error("VC.dat not found")
			return

		line_count = 0
		while True:
			line_string = ad_file.readline().replace('\n', '')
			line_count += 1
			if line_count % 100 == 0:
				logging.info(f"Parsing line {line_count}")
			line_string = line_string.replace('\\', '')
			line_string = line_string.replace("'", "\\'")
			line = line_string.split('|')

			if len(line) <= 1:
				self._db.commit()
				break

			if line[5] != '':
				line[5] = f"'{line[5]}'"
			else:
				line[5] = 'NULL'

			try:
				self._db.execute_query(f"""INSERT INTO vc_vanity_call_sign (
										unique_identifier,
										uls_file_number,
										order_preference,
										requested_call_sign)
										VALUES('{line[1]}', '{line[2]}', '{line[4]}', {line[5]})
										ON DUPLICATE KEY UPDATE `unique_identifier`={line[1]}, `order_preference`={line[4]}
										""", False)

				if line_count % 500 == 0:
					logging.info("Committing!")
					self._db.commit()

			except Exception as ex:
				logging.error(f"Error on line: ```{line_string}```", ex)
				raise ex
		ad_file.close()

	@staticmethod
	def _mysql_date_str(string_val):
		if string_val == '':
			return 'NULL'
		else:
			return f"STR_TO_DATE('{string_val}','%m/%d/%Y')"
