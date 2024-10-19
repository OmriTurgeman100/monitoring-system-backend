create table nodes (
	node_id SERIAL PRIMARY KEY,
	parent INTEGER REFERENCES nodes(node_id),
	title VARCHAR(50),
	description VARCHAR(50),
	status VARCHAR(50) DEFAULT 'expired',
	time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);