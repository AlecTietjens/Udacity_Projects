#Full Stack Nanodegree Project 5 - Linux Web Server Config

## Summary:
An AWS server has been set up set that users can publicly access the Catalog app
developed for Project 3 in the Fullstack Nanodegree program. The app allows users to log
in and create categories and items to add to each category. The user can also edit and 
delete categories and items. Users log in with Google OAuth. Core technologies used 
include Linux (Ubuntu), Python, PostgreSQL, Apache, Flask.
 
## Info for Users and Reviewers:
 - IP Address/SSH Port: 52.36.138.166:2200
 - URL: http://ec2-52-36-138-166.us-west-2.compute.amazonaws.com/

## Software Installed:
 - **apt-get**
 	- libapache2-mod-wsgi
 	- postgresql
 	- git
 	- python-flask
 	- python-sqlalchemy
 	- python-pip
 	- python-psycopg2
 	- python-libpq-dev
 	
 - **pip-install**
	- oauth2client
	- psycopg2
	- requests

## Config Changes:
 - Added root and grader users to PostgreSQL
 - Set the Flask application pulled from Github to use port 80
 - Created a Catalog database
 
## Third Party Resources:
I used Stackoverflow for questions concerning Postgres setup; I didn't realize I had to
create a root user to do config while using root.