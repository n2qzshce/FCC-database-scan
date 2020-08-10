from mysql_connector import MySqlConnector
from fcc_download import HamData


def main():
	fcc_download = HamData()
	# fcc_download.download_and_extract_day('mon')
	fcc_download.import_data()
	print("Success")


main()
