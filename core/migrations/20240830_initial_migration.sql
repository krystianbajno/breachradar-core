CREATE TABLE IF NOT EXISTS credential_patterns (
    id SERIAL PRIMARY KEY,
    pattern TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS scrapes (
    id SERIAL PRIMARY KEY,
    hash VARCHAR(64) NOT NULL,
    source VARCHAR NOT NULL,
    filename VARCHAR,
    file_path TEXT,
    scrape_time TIMESTAMP DEFAULT NOW(),
    state VARCHAR NOT NULL,
    timestamp TIMESTAMP,
    occurrence_time TIMESTAMP,
    processing_start_time TIMESTAMP,
    content BYTEA,
    elastic_id VARCHAR
);

CREATE INDEX IF NOT EXISTS idx_scrapes_hash ON scrapes(hash);
CREATE INDEX IF NOT EXISTS idx_scrapes_state ON scrapes(state);
CREATE INDEX IF NOT EXISTS idx_scrapes_timestamp ON scrapes(timestamp);

CREATE TABLE IF NOT EXISTS identities (
    service VARCHAR NOT NULL,
    nickname VARCHAR NOT NULL,
    cookie TEXT,
    PRIMARY KEY (service, nickname)
);
