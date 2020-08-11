import mysql.connector


def chars(first, last):
	first_ord = ord(first)
	last_ord = ord(last)
	result = set()
	for x in range(first_ord, last_ord):
		result.add(chr(x))
	return result


def scan_existing_handles():
	handles = set()
	# use fcc_amateur;select en.callsign, am.class, full_name, address1, city, state, zip, former_call from en, am, hd
	# where en.fccid=am.fccid and en.fccid=hd.fccid and hd.status=\"A\" and en.callsign=\"$CALLSIGN\"

	connection = mysql.connector.connect(host='127.0.0.1',
											database='fcc_amateur',
											user='root',
											password='a')
	query = "select en.callsign, am.class, full_name, address1, city, state, zip, former_call from en, am, hd " \
			"where en.fccid=am.fccid and en.fccid=hd.fccid and hd.status=\"A\""
	cursor = connection.cursor()
	cursor.execute(query)
	mod_ten = 0
	for record in cursor:
		if mod_ten == 0:
			print(record)
		mod_ten = (mod_ten + 1) % 10
		handles.add(record[0])
	cursor.close()

	return handles


def get_possibles(*character_rules):
	character_rules = list(character_rules)
	possibles = set()

	if len(character_rules) == 1:
		for x in character_rules[0]:
			possibles.add(str(x))
		return possibles

	for x in character_rules[0]:
		sub_possibles = get_possibles(*character_rules[1:])
		for y in sub_possibles:
			possibles.add(str(x) + str(y))
	return possibles


def get_banned(handles_set):
	banned = set()

	# 1.  KA2AA-KA9ZZ, KC4AAA-KC4AAF, KC4USA-KC4USZ, KG4AA-KG4ZZ,
	#           KC6AA-KC6ZZ, KL9KAA- KL9KHZ, KX6AA-KX6ZZ;
	banned_handles = set()
	banned_handles = banned_handles.union(get_possibles({'KA'}, chars('2', '9'), chars('A', 'Z'), chars('A', 'Z')))
	banned_handles = banned_handles.union(get_possibles({'KC4AA'}, chars('A', 'F')))
	banned_handles = banned_handles.union(get_possibles({'KC4US'}, chars('A', 'Z')))
	banned_handles = banned_handles.union(get_possibles({'KG4'}, chars('A', 'Z'), chars('A', 'Z')))
	banned_handles = banned_handles.union(get_possibles({'KC6'}, chars('A', 'Z'), chars('A', 'Z')))
	banned_handles = banned_handles.union(get_possibles({'KL9K'}, chars('A', 'H'), chars('A', 'Z')))
	banned_handles = banned_handles.union(get_possibles({'KX6'}, chars('A', 'Z'), chars('A', 'Z')))
	banned_handles_contained = handles_set.intersection(banned_handles)
	banned = banned.union(banned_handles_contained)

	# 2.  Any call sign having the letters SOS or QRA-QUZ as the suffix;
	banned_suffixes = get_possibles({'Q'}, chars('R', 'U'), chars('A', 'Z'))
	banned_suffixes.add('SOS')
	for x in handles_set:
		if len(x) >= 3:
			end = x[-3:]
			if end in banned_suffixes:
				banned.add(x)

	# 3.  Any call sign having the letters AM-AZ as the prefix (these prefixes
	#           are assigned to other countries by the ITU);
	banned_prefixes = get_possibles({'A'}, chars('M', 'Z'))
	for x in handles_set:
		if len(x) >= 2:
			beginning = x[0:2]
			if beginning in banned_prefixes:
				banned.add(x)

	# 4.  Any 2-by-3 format call sign having the letter X as the first letter of the suffix;
	for x in handles_set:
		if len(x) == 6 and x[2] in chars('0', '9') and x[3] == 'X':
			banned.add(x)

	# 5.  Any 2-by-3 format call sign having the letters AF, KF, NF, or WF as the prefix
	#           and the letters EMA as the suffix (U.S Government FEMA stations);
	banned_handles = get_possibles({'A', 'K', 'N', 'W'}, 'F', chars('0', '9'), {'EMA'})
	banned_handles_contained = banned_handles.intersection(handles_set)
	banned = banned.union(banned_handles_contained)

	banned_prefixes = set()
	# 6.  Any 2-by-3 format call sign having the letters AA-AL as the prefix;
	# 7.  Any 2-by-3 format call sign having the letters NA-NZ as the prefix;
	# 8.  Any 2-by-3 format call sign having the letters WC, WK, WM, WR, or WT
	#           as the prefix (Group X call signs);
	banned_prefixes = banned_prefixes.union(get_possibles({'A', 'K', 'N', 'W'}, chars('A', 'L')))
	banned_prefixes = banned_prefixes.union(get_possibles({'N'}, chars('A', 'Z')))
	banned_prefixes = banned_prefixes.union({'WC', 'WK', 'WM', 'WR', 'WT'})
	for x in handles_set:
		if len(x) == 6 and x[2] in chars('0', '9') and x[0:2] in banned_prefixes:
			banned.add(x)

	# 9.  Any 2-by-3 format call sign having the letters KP, NP or WP as the prefix
	#           and the numeral 0, 6, 7, 8 or 9;
	# 10.  Any 2-by-2 format call sign having the letters KP, NP or WP as the prefix
	#           and the numeral 0, 6, 7, 8 or 9;
	# 11.  Any 2-by-1 format call sign having the letters KP, NP or WP as the prefix
	#           and the numeral 0, 6, 7, 8 or 9;
	banned_prefixes = get_possibles({'K', 'N', 'W'}, {'P'}, {'0', '6', '7', '8', '9'})
	for x in handles_set:
		if len(x) >= 3:
			beginning = x[0:3]
			if beginning in banned_prefixes:
				banned.add(x)

	# 12.  Call signs having the single letter prefix (K, N or W), a single digit numeral
	#           0, 1, 2, 3, 4, 5, 6, 7, 8, 9 and a single letter suffix are reserved for the
	#           special event call sign system.
	banned = banned.intersection(get_possibles({'K', 'N', 'W'}, chars('0', '9')))

	return banned


def main():
	possibles = set()
	handles_1x2 = get_possibles({"K", "N"}, chars('0', '9'), chars('A', 'Z'), chars('A', 'Z'))
	handles_2x1 = get_possibles({"A", "K", "N"}, chars('A', 'Z'), chars('0', '9'), chars('A', 'Z'))
	# handles_2x2 = get_possibles({"A"}, chars('A', 'Z'), chars('0', '9'), chars('A', 'Z'), chars('A', 'Z'))
	possibles = possibles.union(handles_1x2, handles_2x1)

	banned_handles = get_banned(possibles)
	before_len = len(possibles)
	possibles.difference_update(banned_handles)
	after_len = len(possibles)
	print(f"Removed {before_len - after_len} banned.")

	before_len = len(possibles)
	existing = scan_existing_handles()
	possibles.difference_update(existing)
	after_len = len(possibles)
	print(f"Removed {before_len - after_len} existing.")

	f = open("possibles.txt", "w+")
	for x in sorted(possibles):
		f.write(f"{x}\n")
	f.close()

	return


main()
