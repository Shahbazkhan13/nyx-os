-- NyxOS Universal Data Model
-- STEP 06: initial schema skeleton

CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    role TEXT NOT NULL DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE cases (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE assets (
    id INTEGER PRIMARY KEY,
    case_id INTEGER REFERENCES cases(id),
    type TEXT NOT NULL,
    identifier TEXT NOT NULL,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE findings (
    id INTEGER PRIMARY KEY,
    case_id INTEGER REFERENCES cases(id),
    asset_id INTEGER REFERENCES assets(id),
    title TEXT NOT NULL,
    severity TEXT,
    risk_score REAL,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE evidence (
    id INTEGER PRIMARY KEY,
    finding_id INTEGER REFERENCES findings(id),
    type TEXT NOT NULL,
    content TEXT,
    hash TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tools (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    version TEXT,
    category TEXT,
    enabled INTEGER DEFAULT 1
);
