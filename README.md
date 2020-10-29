# FCC-database-scan
This is a tool for scanning the FCC database to search for existing handles

## Usage
To use this tool, you will first need to launch docker-compose for the mysql connection (configurable MySQL coming soon) and then run the main.py.

### Updating possible handles
By default, this program will output a list of all available 4-character and 5-character HAM handles. If you want to change which handles you scan for, you can update
the "generate_vanity_handles" method with your own use of "generate_possibles."

`generate_possibles` accepts multiple sets describing which characters in sequence. `chars_through` will return a set with all characters between and including the digits
specified (e.g. `chars_through('A','C')` returns `{'A','B','C'}`

### Contributing
I'd love some contributors to this project, especially helping make a more user-friendly UI system. If you'd like to contribute to this project, please contact me and make a pull
request!
