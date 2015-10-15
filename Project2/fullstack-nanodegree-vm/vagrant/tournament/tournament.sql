-- Table definitions for the tournament project.
--
-- Author: Alec Tietjens
-- Date: 10/14/2015


DROP DATABASE IF EXISTS tournament;

CREATE DATABASE tournament;

\c tournament;

CREATE TABLE player (
	id SERIAL PRIMARY KEY,
	name TEXT NOT NULL
);

CREATE TABLE match (
	id SERIAL PRIMARY KEY,
	winner_id INT NOT NULL,
	loser_id INT NOT NULL,
    FOREIGN KEY(winner_id) REFERENCES player(id),
    FOREIGN KEY(loser_id) REFERENCES player(id)
);

-- Create a view so that a table doesn't have to be updated for every new match or player
CREATE VIEW standings AS
    SELECT  p.id, 
            p.name, 
            COUNT(m.winner_id) AS wins, 
            (SELECT COUNT(*) FROM match WHERE winner_id = p.id OR loser_id = p.id)
    FROM player AS p
    LEFT OUTER JOIN match AS m
    ON m.winner_id = p.id
    GROUP BY p.id
    ORDER BY wins DESC