# FCC-database-scan
This is a tool for scanning the FCC database to search for available vanity handles. This program is designed to respect all FCC rules regarding available handles, and automatically remove any that are existing or that are allocated to another user and have not lapsed their grace period. 
Handles that are in the `possibles.txt` are available for application IMMEDIATELY.

## Usage
To use this tool, you will first need to launch the docker-compose for the mysql database (configurable MySQL coming soon) and then run the main.py.

### Updating possible handles
By default, this program will output a list of all available 4-character and 5-character HAM handles. If you want to change which handles you scan for, you can update
the "generate_vanity_handles" method with your own use of "generate_possibles."

`vanity_search.py generate_possibles` accepts multiple sets describing which characters in sequence. `chars_through` will return a set with all characters between and including the digits
specified (e.g. `chars_through('A','C')` returns `{'A','B','C'}`

### Searching for your handle (Example)

If you'd like to search for a 1x2 handle, you will need to modify `vanity_search.py generate_vanity_handles` like so:
```def generate_vanity_handles(self):
		possibles = set()
		handles_1x2 = self.generate_possibles({"K", "N", "W"}, self.chars_through('0', '9'), self.chars_through('A', 'Z'),
												self.chars_through('A', 'Z'))
		possibles = possibles.union(handles_1x2)
```
Illegal/taken/invalid handles will be automatically pruned. (THERE'S NOT MANY 1X2'S OR 2X1'S AVAILABLE)

### Output
The `possibles.txt` will output a list of all available handles. If there are outstanding applications for those handles, the LOWEST RANKING preference and the EARLIEST application date will be shown. THESE MAY NOT BE THE SAME APPLICATIONS. If someone submitted preference 25 on 5-21-2020 and someone else submitted preference 3 on 6-14-2020, the output will show `{SOME HANDLE}     2020-05-21     3`

This program is extremely conservative with saying a handle is available. It is a mostly-comprehensive list but additional handles may be available outside of this list.

### Contributing
I'd love some contributors to this project, especially helping make a more user-friendly UI system. If you'd like to contribute to this project, please contact me and make a pull
request!

### Facts for nerds
This program downloads the weekly database dump from the FCC and creates a local replica of data relevant to handles locally. This includes applications, licenses, and the contents of applications with ham preference data. The data is then compiled into a database created from the FCC's ULS license definitions, and then queries are built locally.

### Success stories
This application helped me get a vanity handle of my choosing on only my second attempt. The first attempt I lost on a 50/50 draw from an application on the same day, which is just poor luck. Before this, I had tried to apply 5 times for a vanity handle and they were rejected.
