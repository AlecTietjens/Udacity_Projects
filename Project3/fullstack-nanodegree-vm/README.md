Project Three
=============

Files included:  
application.py - controller for application  
DAL.py - data access layer for application (ORM)  
create_catalog_db.sql - SQL script to create database for project  
*client_secrets.json - Used for Google OAuth... this will need to be replaced with client_secrets created through your own Google dev console  
  
For this project you will need to initialize a database with create_catalog_db.sql. After that you will be able to launch application.py to start the web server and make requests against the machine. I used Vagrant to make setting up a virtual machine less effortful. The files are located in vagrant/catalog/  
  
This project requires apt-get of PostgreSQL, Python, python-flask, python-sqlalchemy, and python-pip. It will need pip install of oauth2client, requests, and httplib2.  
  
Create the database by executing the following commands:  
  
psql  
\i create_catalog_db.sql  

To run the web server, execute the command 'python application.py'

You can now go to the URL for the server, which on a local machine would be localhost:5000 (it uses port 5000 as default currently). You can view the website or make API calls to the application - the application can return both JSON and XML. If API calls are made, the application defaults to JSON
unless the URL is appended with XML, e.g., localhost:5000/catalog/api and localhost:5000/catalog/api/json will return JSON and localhost:5000/catalog/api/xml will return XML.  
  
Sources used:  
http://flask.pocoo.org/  
http://docs.sqlalchemy.org/en/latest/dialects/postgresql.html  
https://github.com/udacity/ud330/tree/master/Lesson4/step2  
https://developer.mozilla.org/en-US/docs/Web/HTTP/data_URIs