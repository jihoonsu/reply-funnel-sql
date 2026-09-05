-- Do decision-makers reply more than individual contributors?
--
-- reply_rate_per_open is the measure that matters. If one group simply opens
-- more email, a per-send rate would credit that difference to seniority when
-- it actually belongs to the open step.
SELECT c.seniority,
       COUNT(*)                                              AS sends,
       SUM(s.opened)                                         AS opens,
       SUM(s.replied)                                        AS replies,
       ROUND(100.0 * SUM(s.replied) / COUNT(*), 2)           AS reply_rate_per_send_pct,
       ROUND(100.0 * SUM(s.replied) / SUM(s.opened), 2)      AS reply_rate_per_open_pct
FROM sends s
JOIN contacts c ON c.id = s.contact_id
GROUP BY c.seniority
ORDER BY reply_rate_per_open_pct DESC;
