import sqlite3
import os
import sys

with open(os.path.join(sys.path[0], "ddl.sql"), "r") as f:
	script_lines = [l for l in f.readlines() if not l.startswith('--') and l.lstrip() != '']
	conn = sqlite3.connect('pubsub.db')
	cursor = conn.cursor()

	for script_line in script_lines:
		cursor.execute(script_line)
	conn.close()
