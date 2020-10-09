import logging
import sys


class Logger:
	_spans = None

	@classmethod
	def __init__(cls, level=logging.INFO):
		logging.basicConfig(level=logging.INFO,
							format="[%(asctime)s] %(levelname)s [%(filename)s.%(funcName)s:%(lineno)d] %(message)s",
							datefmt="%H:%M:%S",
							stream=sys.stdout)
		logging.info("Logger initialized")
