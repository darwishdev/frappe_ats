DROP FUNCTION IF EXISTS get_job_opening_step_stats;
DELIMITER $$
CREATE OR REPLACE FUNCTION get_job_opening_step_stats(job_names text)
RETURNS JSON
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE result JSON;

    WITH steps AS (
        SELECT
            s.parent,
            s.step_name,
            s.step_code,
            COALESCE(COUNT(a.name), 0) applicants_count
        FROM `tabPipeline Step` s
        LEFT JOIN `tabJob Opening Applicant` a
            ON s.name = a.step
           AND a.invalidated_at IS NULL
        WHERE s.parenttype = 'Job Opening'
        AND (
            job_names IS NULL
            OR FIND_IN_SET(s.parent, job_names) > 0
        )
      GROUP BY s.parent, s.step_name, s.step_code
    ),
    steps_agg AS (
        SELECT
            parent,
            JSON_ARRAYAGG(
                JSON_OBJECT(
                    'step_name', step_name,
                    'step_code', step_code,
                    'applicants_count', applicants_count
                )
            ) AS steps
        FROM steps
        GROUP BY parent
    )
    SELECT JSON_OBJECTAGG(parent, steps)
    INTO result
    FROM steps_agg;

    RETURN result;
END$$

DELIMITER ;
