import asyncio
import datetime
import logging

from Logger import Logger
from fcc_download import HamData
from fcc_download import RunType
from vanity_search import VanitySearch


def download_fcc_data():
	fcc_download = HamData(log_line_interval=20000)
	fcc_download.cleanup_downloads()
	today = datetime.date.today()

	last_week_run = fcc_download.get_last_run_time(RunType.WEEK)
	sunday = today - datetime.timedelta(days=today.weekday() + 1)

	if last_week_run is None or last_week_run < sunday:
		logging.info(f"Last week run: {last_week_run}")
		fcc_download.download_and_import_week()
	else:
		logging.info("Skipping week download")

	last_day_run = fcc_download.get_last_run_time(RunType.DAY)

	for weekday_num in range(1, today.isoweekday()):
		date_to_use = today.isocalendar()
		run_date = datetime.date.fromisocalendar(year=date_to_use[0], week=date_to_use[1], day=weekday_num)

		if last_day_run is not None and run_date <= last_day_run:
			logging.info(f"Skipping day run: {run_date}")
			continue

		fcc_download.download_and_import_day(run_date)

		if run_date >= today:
			break

	fcc_download.cleanup_downloads()

	del fcc_download


def run_vanity_search():
	vanity_search = VanitySearch()
	vanity_search.generate_vanity_handles()


def main():
	Logger(level=logging.INFO)
	download_fcc_data()
	run_vanity_search()


main()
