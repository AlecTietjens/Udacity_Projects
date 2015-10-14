-- Table definitions for the tournament project.
--
-- Author: Alec Tietjens
-- Date: 09/28/2015


DROP DATABASE IF EXISTS Tournament;

CREATE DATABASE Tournament;

\c tournament;

CREATE TABLE Player (
	ID SERIAL PRIMARY KEY,
	Name TEXT NOT NULL
);

CREATE TABLE Match (
	ID SERIAL PRIMARY KEY,
	WinnerID INT NOT NULL,
	LoserID INT NOT NULL
);

CREATE TABLE Standings (
    ID SERIAL PRIMARY KEY,
	PlayerName TEXT NOT NULL,
	PlayerID INT NOT NULL,
	Wins INT DEFAULT 0,
	Matches INT DEFAULT 0
);