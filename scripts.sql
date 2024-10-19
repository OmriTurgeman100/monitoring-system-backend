create table nodes (
	node_id SERIAL PRIMARY KEY,
	parent INTEGER REFERENCES nodes(node_id) ON DELETE CASCADE,
	title VARCHAR(50) NOT NULL,
	description VARCHAR(50) NOT NULL,
	status VARCHAR(50) DEFAULT 'expired',
    excluded VARCHAR(50) DEFAULT 'false',
	time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

create table reports (
	id SERIAL PRIMARY KEY,
	report_id VARCHAR(50) NOT NULL,
	parent INTEGER REFERENCES nodes(node_id) ON DELETE CASCADE,
	title VARCHAR(50) NOT NULL,
	description VARCHAR(50) NOT NULL,
	value INTEGER,
	time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE report_rules (
    rule_id SERIAL PRIMARY KEY,
    report_id VARCHAR(50) NOT NULL,
    condition_operator VARCHAR(10) NOT NULL, 
    threshold INTEGER NOT NULL,
    action VARCHAR(50) NOT NULL, 
    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
