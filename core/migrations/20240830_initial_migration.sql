CREATE TABLE IF NOT EXISTS scrapes (
    hash VARCHAR PRIMARY KEY,
    source VARCHAR,
    filename VARCHAR,
    file_path TEXT,
    scrape_time TIMESTAMP DEFAULT NOW(),
    state VARCHAR,
    parent_scrape_id VARCHAR REFERENCES scrapes(hash)
);

CREATE TABLE IF NOT EXISTS identities (
    service VARCHAR,
    nickname VARCHAR,
    cookie TEXT,
    PRIMARY KEY (service, nickname)
);
