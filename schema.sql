CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    name TEXT,
    client TEXT,
    start_date DATE,
    duration_months INT,
    currency TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS budget_items (
    id SERIAL PRIMARY KEY,
    project_id INT DEFAULT 1,
    sl_no INT,
    description TEXT,
    responsible_agency TEXT,
    qty FLOAT,
    duration_text TEXT,
    weight_kg FLOAT,
    total_weight_kg FLOAT,
    unit_rate_inr FLOAT,
    total_budget FLOAT,
    computed_total FLOAT,
    needs_review BOOLEAN,
    raw_file TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
