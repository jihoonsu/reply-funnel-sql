-- Does a longer follow-up sequence help, or just annoy people?
--
-- Sends fall off at later touches because most sequences stop early, so the
-- sample size column matters as much as the rate here.
SELECT s.touch_number,
       COUNT(*)                                         AS sends,
       SUM(s.opened)                                    AS opens,
       SUM(s.replied)                                   AS replies,
       ROUND(100.0 * SUM(s.replied) / COUNT(*), 2)      AS reply_rate_per_send_pct,
       ROUND(100.0 * SUM(s.replied) / SUM(s.opened), 2) AS reply_rate_per_open_pct
FROM sends s
GROUP BY s.touch_number
ORDER BY s.touch_number;
