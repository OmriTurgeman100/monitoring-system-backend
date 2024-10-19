create table reports (
	id SERIAL PRIMARY KEY,
	report_id VARCHAR(50) NOT NULL,
	parent INTEGER REFERENCES nodes(node_id),
	title VARCHAR(50),
	description VARCHAR(50),
	value INTEGER,
	time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

