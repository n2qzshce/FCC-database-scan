from fcc_download import HamData
from mysql_connector import MySqlConnector


def main():
	mysql_connector = MySqlConnector('127.0.0.1', 'fcc_amateur', 'root', 'a')
	mysql_connector.execute_query("DROP SCHEMA fcc_amateur")
	del mysql_connector

	fcc_download = HamData()
	fcc_download.cleanup_downloads()

	fcc_download.download_and_extract_week()
	fcc_download.import_data()
	fcc_download.cleanup_downloads()

	fcc_download.download_and_extract_day('sun')
	fcc_download.import_data()
	fcc_download.cleanup_downloads()

	fcc_download.download_and_extract_day('mon')
	fcc_download.import_data()
	fcc_download.cleanup_downloads()
	del fcc_download


main()
