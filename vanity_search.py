import datetime
import logging

from mysql_connector import MySqlConnector


class VanitySearch:
	_mysql_connector = None
	
	def __init__(self):
		self._mysql_connector = MySqlConnector('127.0.0.1', 'fcc_amateur', 'root', 'a')
	
	def generate_possibles(self, *character_rules):
		character_rules = list(character_rules)
		possibles = set()

		if len(character_rules) == 1:
			for x in character_rules[0]:
				possibles.add(str(x))
			return possibles

		for x in character_rules[0]:
			sub_possibles = self.generate_possibles(*character_rules[1:])
			for y in sub_possibles:
				possibles.add(str(x) + str(y))
		return possibles

	def get_banned_handles(self, handles_set):
		banned = set()

		# 1.  KA2AA-KA9ZZ, KC4AAA-KC4AAF, KC4USA-KC4USZ, KG4AA-KG4ZZ,
		#           KC6AA-KC6ZZ, KL9KAA- KL9KHZ, KX6AA-KX6ZZ;
		banned_handles = set()
		banned_handles = banned_handles.union(self.generate_possibles({'KA'}, self.chars_through('2', '9'), self.chars_through('A', 'Z'), self.chars_through('A', 'Z')))
		banned_handles = banned_handles.union(self.generate_possibles({'KC4AA'}, self.chars_through('A', 'F')))
		banned_handles = banned_handles.union(self.generate_possibles({'KC4US'}, self.chars_through('A', 'Z')))
		banned_handles = banned_handles.union(self.generate_possibles({'KG4'}, self.chars_through('A', 'Z'), self.chars_through('A', 'Z')))
		banned_handles = banned_handles.union(self.generate_possibles({'KC6'}, self.chars_through('A', 'Z'), self.chars_through('A', 'Z')))
		banned_handles = banned_handles.union(self.generate_possibles({'KL9K'}, self.chars_through('A', 'H'), self.chars_through('A', 'Z')))
		banned_handles = banned_handles.union(self.generate_possibles({'KX6'}, self.chars_through('A', 'Z'), self.chars_through('A', 'Z')))
		banned_handles_contained = handles_set.intersection(banned_handles)
		banned = banned.union(banned_handles_contained)

		# 2.  Any call sign having the letters SOS or QRA-QUZ as the suffix;
		banned_suffixes = self.generate_possibles({'Q'}, self.chars_through('R', 'U'), self.chars_through('A', 'Z'))
		banned_suffixes.add('SOS')
		for x in handles_set:
			if len(x) >= 3:
				end = x[-3:]
				if end in banned_suffixes:
					banned.add(x)

		# 3.  Any call sign having the letters AM-AZ as the prefix (these prefixes
		#           are assigned to other countries by the ITU);
		banned_prefixes = self.generate_possibles({'A'}, self.chars_through('M', 'Z'))
		for x in handles_set:
			if len(x) >= 2:
				beginning = x[0:2]
				if beginning in banned_prefixes:
					banned.add(x)

		# 4.  Any 2-by-3 format call sign having the letter X as the first letter of the suffix;
		for x in handles_set:
			if len(x) == 6 and x[2] in self.chars_through('0', '9') and x[3] == 'X':
				banned.add(x)

		# 5.  Any 2-by-3 format call sign having the letters AF, KF, NF, or WF as the prefix
		#           and the letters EMA as the suffix (U.S Government FEMA stations);
		banned_handles = self.generate_possibles({'A', 'K', 'N', 'W'}, 'F', self.chars_through('0', '9'), {'EMA'})
		banned_handles_contained = banned_handles.intersection(handles_set)
		banned = banned.union(banned_handles_contained)

		banned_prefixes = set()
		# 6.  Any 2-by-3 format call sign having the letters AA-AL as the prefix;
		# 7.  Any 2-by-3 format call sign having the letters NA-NZ as the prefix;
		# 8.  Any 2-by-3 format call sign having the letters WC, WK, WM, WR, or WT
		#           as the prefix (Group X call signs);
		banned_prefixes = banned_prefixes.union(self.generate_possibles({'A', 'K', 'N', 'W'}, self.chars_through('A', 'L')))
		banned_prefixes = banned_prefixes.union(self.generate_possibles({'N'}, self.chars_through('A', 'Z')))
		banned_prefixes = banned_prefixes.union({'WC', 'WK', 'WM', 'WR', 'WT'})
		for x in handles_set:
			if len(x) == 6 and x[2] in self.chars_through('0', '9') and x[0:2] in banned_prefixes:
				banned.add(x)

		# 9.  Any 2-by-3 format call sign having the letters KP, NP or WP as the prefix
		#           and the numeral 0, 6, 7, 8 or 9;
		# 10.  Any 2-by-2 format call sign having the letters KP, NP or WP as the prefix
		#           and the numeral 0, 6, 7, 8 or 9;
		# 11.  Any 2-by-1 format call sign having the letters KP, NP or WP as the prefix
		#           and the numeral 0, 6, 7, 8 or 9;
		banned_prefixes = self.generate_possibles({'K', 'N', 'W'}, {'P'}, {'0', '6', '7', '8', '9'})
		for x in handles_set:
			if len(x) >= 3:
				beginning = x[0:3]
				if beginning in banned_prefixes:
					banned.add(x)

		# 12.  Call signs having the single letter prefix (K, N or W), a single digit numeral
		#           0, 1, 2, 3, 4, 5, 6, 7, 8, 9 and a single letter suffix are reserved for the
		#           special event call sign system.
		short_handles = self.generate_possibles({'K', 'N', 'W'}, self.chars_through('0', '9'))
		short_banned = short_handles.intersection(handles_set)
		banned = banned.union(short_banned)

		# Two letter prefixes that are designed for regions 11-13 are not available in regions
		# 1-10.
		regionals = self.generate_possibles({'AL', 'KL', 'NL', 'WL', 'KP', 'NP', 'WP',
														'AH', 'KH', 'NH', 'WH'}, self.chars_through('0', '9'),
														self.chars_through('A', 'Z'))
		regional_banned = regionals.intersection(handles_set)
		banned = banned.union(regional_banned)

		return banned

	# noinspection PyMethodMayBeStatic
	def chars_through(self, first, last):
		first_ord = ord(first)
		last_ord = ord(last)
		result = set()
		for x in range(first_ord, last_ord):
			result.add(chr(x))
		return result

	def scan_existing_handles(self, possibles_list):
		possibles_str = "','".join(possibles_list)
		possibles_str = "'" + possibles_str + "'"
		query = f"""select hd_license_header.call_sign,expired_date from hd_license_header
					where hd_license_header.expired_date >= DATE_SUB(NOW(), INTERVAL 24 MONTH)
					AND hd_license_header.call_sign in ({possibles_str});"""
		self._mysql_connector.execute_query(query, False)
		row = self._mysql_connector.fetchone()

		existing = set()
		while True:
			row = self._mysql_connector.fetchone()
			if row is None:
				break
			existing.add(row[0])

		return existing

	def scan_license_applications(self, possibles_list):
		possibles_str = "','".join(possibles_list)
		possibles_str = "'" + possibles_str + "'"
		query = f"""select ad_application_detail.unique_identifier, ad_application_detail.uls_file_number, 
					ad_application_detail.receipt_date, vc_vanity_call_sign.requested_call_sign, vc_vanity_call_sign.
					order_preference from ad_application_detail join vc_vanity_call_sign on ad_application_detail.
					unique_identifier=vc_vanity_call_sign.unique_identifier where 
					ad_application_detail.receipt_date >= DATE_SUB(NOW(), INTERVAL 25 DAY) and 
					vc_vanity_call_sign.requested_call_sign in ({possibles_str});"""
		self._mysql_connector.execute_query(query, False)
		row = self._mysql_connector.fetchone()

		lowest_rank = dict.fromkeys(possibles_list)
		for x in lowest_rank:
			lowest_rank[x] = dict({'preference': None, 'date': None})

		while True:
			if row is None:
				break

			order_pref = lowest_rank[row[3]]
			if order_pref['date'] is None or row[2] < order_pref['date']:
				order_pref['date'] = row[2]
				order_pref['preference'] = row[4]
				lowest_rank[row[3]] = order_pref

			row = self._mysql_connector.fetchone()

		return lowest_rank

	def generate_vanity_handles(self):
		possibles = set()
		handles_1x2 = self.generate_possibles({"K", "N", "W"}, self.chars_through('0', '9'), self.chars_through('A', 'Z'),
												self.chars_through('A', 'Z'))
		handles_2x1 = self.generate_possibles({"A", "K", "N", "W"}, self.chars_through('A', 'Z'), self.chars_through('0', '9'),
												self.chars_through('A', 'Z'))
		handles_2x2 = self.generate_possibles({"A", "K", "N", "W"}, self.chars_through('A', 'Z'),
												self.chars_through('0', '9'), self.chars_through('A', 'Z'),
												self.chars_through('A', 'Z'))
		handles_1x3 = self.generate_possibles({"K", "N", "W"}, self.chars_through('0', '9'), self.chars_through('A', 'Z'),
												self.chars_through('A', 'Z'), self.chars_through('A', 'Z'))
		possibles = possibles.union(handles_1x2, handles_2x1)

		banned_handles = self.get_banned_handles(possibles)
		before_len = len(possibles)
		possibles.difference_update(banned_handles)
		after_len = len(possibles)
		logging.info(f"Removed {before_len - after_len} banned.")

		before_len = len(possibles)
		existing = self.scan_existing_handles(possibles)
		possibles.difference_update(existing)
		after_len = len(possibles)
		logging.info(f"Removed {before_len - after_len} existing.")

		license_data = self.scan_license_applications(possibles)

		f = open("possibles.txt", "w+")
		for x in sorted(license_data):
			date_pref = license_data[x]['date']
			date_preference = date_pref if date_pref is not None else 'n/a'
			order_pref = license_data[x]['preference']
			order_preference = order_pref if order_pref is not None else 'n/a'
			f.write(f"{x}\t{date_preference}\t{order_preference}\n")
		f.close()

		return

