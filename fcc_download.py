import shutil
import zipfile
from urllib import request


class FccDownload:
	_FULL_URL = "ftp://wirelessftp.fcc.gov/pub/uls/complete/l_amat.zip"
	_DAY_TEMPLATE_URL = "ftp://wirelessftp.fcc.gov/pub/uls/daily/l_ac_{day}.zip"

	def __init__(self):
		return

	def download_and_extract_day(self, day):
		file_dir = 'download'
		day_url_path = self._DAY_TEMPLATE_URL.format(day=day)
		local_path = f'{file_dir}/l_ac_{day}.zip'

		print(f"Downloading from {day_url_path}")
		data_file = request.urlopen(day_url_path)

		print(f"Writing to {local_path}")
		local_file = open(local_path, 'wb')
		shutil.copyfileobj(data_file, local_file)

		print(f"Unzipping to {file_dir}")
		zip_ref = zipfile.ZipFile(local_path, 'r')
		zip_ref.extractall(file_dir)


def main():
	fcc_download = FccDownload()
	fcc_download.download_and_extract_day("mon")


main()