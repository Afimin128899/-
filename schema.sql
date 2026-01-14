CREATE TABLE users (
    tg_id BIGINT PRIMARY KEY,
    balance INT DEFAULT 0,
    referrer_id BIGINT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE tasks (
    task_key TEXT PRIMARY KEY,
    title TEXT,
    reward INT NOT NULL
);

CREATE TABLE user_tasks (
    tg_id BIGINT,
    task_key TEXT,
    status TEXT,
    PRIMARY KEY (tg_id, task_key)
);

CREATE TABLE balance_logs (
    id SERIAL PRIMARY KEY,
    tg_id BIGINT,
    change INT,
    reason TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE withdraws (
    id SERIAL PRIMARY KEY,
    tg_id BIGINT,
    amount INT,
    status TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE promo_codes (
    code TEXT PRIMARY KEY,
    reward INT,
    uses_left INT
);

CREATE TABLE promo_used (
    tg_id BIGINT,
    code TEXT,
    PRIMARY KEY (tg_id, code)
);

CREATE TABLE support (
    id SERIAL PRIMARY KEY,
    tg_id BIGINT,
    text TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
