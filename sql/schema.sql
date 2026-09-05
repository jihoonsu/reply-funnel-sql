-- Three tables. A company has contacts; a contact receives a sequence of
-- outreach touches ("sends"). Everything downstream is derived from these.

CREATE TABLE companies (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    industry TEXT NOT NULL
);

CREATE TABLE contacts (
    id INTEGER PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    name TEXT NOT NULL,
    title TEXT NOT NULL,
    seniority TEXT NOT NULL CHECK (seniority IN ('decision_maker', 'individual_contributor'))
);

-- One row per email actually sent. touch_number is which email in the
-- sequence this is (1 = first outreach, 2 = first follow-up, ...).
-- replied = 1 requires opened = 1 -- enforced by the generator, not the
-- schema, because SQLite's CHECK can't reference sibling columns portably
-- across the versions this needs to run on.
CREATE TABLE sends (
    id INTEGER PRIMARY KEY,
    contact_id INTEGER NOT NULL REFERENCES contacts(id),
    touch_number INTEGER NOT NULL,
    sent_at TEXT NOT NULL,
    opened INTEGER NOT NULL CHECK (opened IN (0, 1)),
    replied INTEGER NOT NULL CHECK (replied IN (0, 1))
);

CREATE INDEX idx_contacts_company ON contacts(company_id);
CREATE INDEX idx_sends_contact ON sends(contact_id);
