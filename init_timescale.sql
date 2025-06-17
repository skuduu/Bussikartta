CREATE EXTENSION IF NOT EXISTS timescaledb;

DROP TABLE IF EXISTS vehicle_positions;

CREATE TABLE vehicle_positions (
    id SERIAL,
    vehicle_id TEXT,
    route_id TEXT,
    lat DOUBLE PRECISION,
    lon DOUBLE PRECISION,
    bearing DOUBLE PRECISION,
    speed DOUBLE PRECISION,
    timestamp TIMESTAMPTZ NOT NULL
);
-- vehicles
CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id TEXT PRIMARY KEY,
    label TEXT,
    vehicle_type INTEGER,
    capacity INTEGER
);

-- alerts
CREATE TABLE IF NOT EXISTS alerts (
    alert_id SERIAL PRIMARY KEY,
    header_text TEXT,
    description_text TEXT,
    active_start TIMESTAMPTZ,
    active_end TIMESTAMPTZ
);

-- calendar
CREATE TABLE IF NOT EXISTS calendar (
    service_id TEXT PRIMARY KEY,
    monday BOOLEAN,
    tuesday BOOLEAN,
    wednesday BOOLEAN,
    thursday BOOLEAN,
    friday BOOLEAN,
    saturday BOOLEAN,
    sunday BOOLEAN,
    start_date DATE,
    end_date DATE
);

-- fare_attributes
CREATE TABLE IF NOT EXISTS fare_attributes (
    fare_id TEXT PRIMARY KEY,
    price NUMERIC,
    currency_type TEXT,
    payment_method INTEGER,
    transfers INTEGER
);

-- fare_rules
CREATE TABLE IF NOT EXISTS fare_rules (
    fare_id TEXT,
    origin_id TEXT,
    destination_id TEXT,
    contains_id TEXT
);

-- transfers
CREATE TABLE IF NOT EXISTS transfers (
    from_stop_id TEXT,
    to_stop_id TEXT,
    transfer_type INTEGER,
    min_transfer_time INTEGER
);

-- feed_info
CREATE TABLE IF NOT EXISTS feed_info (
    feed_publisher_name TEXT,
    feed_publisher_url TEXT,
    feed_lang TEXT,
    feed_start_date DATE,
    feed_end_date DATE,
    feed_version TEXT
);

-- emissions
CREATE TABLE IF NOT EXISTS emissions (
    vehicle_id TEXT,
    emission_type TEXT,
    emission_value NUMERIC
);
SELECT create_hypertable('vehicle_positions', 'timestamp', if_not_exists => TRUE, create_default_indexes => FALSE);
