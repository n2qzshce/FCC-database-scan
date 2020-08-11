from Logger import Logger
from fcc_download import HamData
from vanity_search import VanitySearch


def download_fcc_data():
	fcc_download = HamData()
	fcc_download.cleanup_downloads()

	fcc_download.download_and_extract_week()
	fcc_download.import_data()
	fcc_download.cleanup_downloads()

	for day in {'sun', 'mon', 'tue'}:
		fcc_download.download_and_extract_day(day)
		fcc_download.import_data()
		fcc_download.cleanup_downloads()

	del fcc_download


def run_vanity_search():
	vanity_search = VanitySearch()
	vanity_search.generate_vanity_handles()


def main():
	Logger()
	# download_fcc_data()
	# run_vanity_search()


main()
