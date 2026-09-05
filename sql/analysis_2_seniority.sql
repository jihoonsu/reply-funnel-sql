-- Reply rate by contact seniority, among opened emails only. This is the
-- query that has to recover planted effect #1: decision-makers should
-- reply substantially more often than individual contributors.
SELECT
    c.seniority,
    COUNT(*) AS opened_sends,
    SUM(s.replied) AS replies,
    ROUND(100.0 * SUM(s.replied) / COUNT(*), 1) AS reply_rate_pct
FROM sends s
JOIN contacts c ON c.id = s.contact_id
WHERE s.opened = 1
GROUP BY c.seniority
ORDER BY reply_rate_pct DESC;
