-- How far does a cold email actually get?
--
-- Both denominators are shown because they answer different questions:
-- pct_of_sent is the yield you get from the whole list, pct_of_previous is
-- where the funnel actually loses people.
WITH totals AS (
    SELECT COUNT(*)       AS sent,
           SUM(opened)    AS opened,
           SUM(replied)   AS replied
    FROM sends
)
SELECT 1 AS ord, 'sent' AS stage, sent AS n,
       ROUND(100.0 * sent / sent, 2)             AS pct_of_sent,
       NULL                                      AS pct_of_previous
FROM totals
UNION ALL
SELECT 2, 'opened', opened,
       ROUND(100.0 * opened / sent, 2),
       ROUND(100.0 * opened / sent, 2)
FROM totals
UNION ALL
SELECT 3, 'replied', replied,
       ROUND(100.0 * replied / sent, 2),
       ROUND(100.0 * replied / opened, 2)
FROM totals
ORDER BY ord;
