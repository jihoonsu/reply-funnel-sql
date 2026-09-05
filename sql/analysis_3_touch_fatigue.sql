-- Reply rate by touch number, among opened emails only. Has to recover
-- planted effect #2: reply rate should decline as the follow-up sequence
-- goes on, not stay flat or rise.
SELECT
    s.touch_number,
    COUNT(*) AS opened_sends,
    SUM(s.replied) AS replies,
    ROUND(100.0 * SUM(s.replied) / COUNT(*), 1) AS reply_rate_pct
FROM sends s
WHERE s.opened = 1
GROUP BY s.touch_number
ORDER BY s.touch_number;
