-- Overall funnel: how many sends were opened, and of those, how many
-- got a reply. The two percentages that matter in cold outreach.
SELECT
    COUNT(*) AS total_sends,
    SUM(opened) AS total_opened,
    SUM(replied) AS total_replied,
    ROUND(100.0 * SUM(opened) / COUNT(*), 1) AS open_rate_pct,
    ROUND(100.0 * SUM(replied) / NULLIF(SUM(opened), 0), 1) AS reply_rate_given_open_pct
FROM sends;
