-- Table definitions for the tournament project.
--
-- Author: Alec Tietjens
-- Date: 09/28/2015


DROP DATABASE IF EXISTS catalog;

CREATE DATABASE catalog;

\c catalog;

CREATE TABLE category (
	id SERIAL PRIMARY KEY,
	name TEXT NOT NULL
);

CREATE TABLE item (
	id SERIAL PRIMARY KEY,
	name TEXT NOT NULL,
    description TEXT NULL,
    category_id INT NOT NULL,
	FOREIGN KEY(category_id) REFERENCES category(id)
);