CREATE TABLE IF NOT EXISTS predictions (
    id          SERIAL PRIMARY KEY,
    created_at  TIMESTAMP DEFAULT NOW(),
    text_input  TEXT,
    predicted_text TEXT,
    predicted_code TEXT,
    predicted_label TEXT,
    model       TEXT,
    feedback    INTEGER,
    copy        BOOLEAN
);
