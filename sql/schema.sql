-- Three tables. companies and contacts describe who was contacted; sends is
-- one row per email actually sent, which is the grain every analysis needs.
DROP TABLE IF EXISTS sends;
DROP TABLE IF EXISTS contacts;
DROP TABLE IF EXISTS companies;

CREATE TABLE companies (
    id       INTEGER PRIMARY KEY,
    name     TEXT NOT NULL,
    industry TEXT NOT NULL
);

CREATE TABLE contacts (
    id         INTEGER PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    email      TEXT NOT NULL UNIQUE,
    seniority  TEXT NOT NULL CHECK (seniority IN ('decision_maker', 'individual_contributor'))
);

CREATE TABLE sends (
    id           INTEGER PRIMARY KEY,
    contact_id   INTEGER NOT NULL REFERENCES contacts(id),
    touch_number INTEGER NOT NULL CHECK (touch_number BETWEEN 1 AND 5),
    sent_on      TEXT NOT NULL,
    -- Stored 0/1 rather than as a status column: an email can be opened and
    -- not replied to, so these are two independent facts, not one state.
    opened       INTEGER NOT NULL CHECK (opened IN (0, 1)),
    replied      INTEGER NOT NULL CHECK (replied IN (0, 1)),
    -- You cannot reply to an email you never opened. Enforcing it here means
    -- the analysis never has to defend against it.
    CHECK (replied = 0 OR opened = 1),
    UNIQUE (contact_id, touch_number)
);

CREATE INDEX idx_sends_contact ON sends(contact_id);
CREATE INDEX idx_contacts_company ON contacts(company_id);
