Project Two
=============

Files included:
tournament.sql
tournament.py
tournament_test.py

For this project I created a database initialization SQL script and completed methods to be used against the database in tournament.py. I used Vagrant to make setting up a virtual machine less effortful.

This project requires PostgreSQL, Python, and python-psycopg2 to be installed. To create the database, execute the following commands..

psql
\i tournament.sql

To run the python tests against the database and python methods used against the database, execute the following command..
python tournament_test.py



Sources used:
http://www.postgresql.org/docs/
http://initd.org/psycopg/docs/