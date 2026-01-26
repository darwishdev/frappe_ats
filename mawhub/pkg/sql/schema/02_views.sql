
CREATE OR REPLACE VIEW tal_job_applicants_view AS
WITH
    applicants AS (
        SELECT
            /* =========================
            Job Opening (j)
            ========================= */
            j.name job_opening_id,
            /* =========================
            Job Pipeline (p)
            ========================= */
            p.name pipeline_id,
            p.description pipeline_description,
            p.is_primary pipeline_is_primary,
            p.docstatus pipeline_docstatus,
            p.creation pipeline_created_at,
            p.modified pipeline_modified_at,
            /* =========================
            Pipeline Step (ps)
            ========================= */
            ps.name pipeline_step_id,
            ps.idx pipeline_step_idx,
            ps.step_name pipeline_step_name,
            ps.step_type pipeline_step_type,
            ps.parent pipeline_parent_id,
            /* =========================
            Job Applicant (a)
            ========================= */
            a.name applicant_id,
            a.applicant_name applicant_name,
            a.email_id applicant_email,
            a.phone_number applicant_phone,
            a.country applicant_country,
            a.job_title applicant_job_title,
            a.designation applicant_designation,
            a.status applicant_status,
            a.source applicant_source,
            a.source_name applicant_source_name,
            a.employee_referral applicant_employee_referral,
            a.applicant_rating applicant_rating,
            a.resume_link applicant_resume_link,
            a.resume_attachment applicant_resume_attachment,
            a.cover_letter applicant_cover_letter,
            a.custom_pipeline_step applicant_pipeline_step_ref,
            a.docstatus applicant_docstatus,
            a.creation applicant_created_at,
            a.modified applicant_modified_at,
            /* =========================
            Interview (i)
            ========================= */
            i.name interview_id,
            i.interview_round interview_round,
            i.status interview_status,
            i.scheduled_on interview_scheduled_on,
            i.from_time interview_from_time,
            i.to_time interview_to_time,
            i.expected_average_rating interview_expected_avg_rating,
            i.average_rating interview_average_rating,
            i.job_opening interview_job_opening,
            i.designation interview_designation,
            i.docstatus interview_docstatus,
            i.creation interview_created_at,
            i.modified interview_modified_at,
            /* =========================
            Interview Feedback (f)
            ========================= */
            f.name feedback_id,
            f.interviewer feedback_interviewer,
            f.result feedback_result,
            f.average_rating feedback_average_rating,
            f.feedback feedback_text,
            f.docstatus feedback_docstatus,
            f.creation feedback_created_at,
            f.modified feedback_modified_at,
            /* =========================
            Appointment Letter (al)
            ========================= */
            al.name appointment_letter_id,
            al.company appointment_company,
            al.appointment_date appointment_date,
            al.appointment_letter_template appointment_template,
            al.docstatus appointment_docstatus,
            al.creation appointment_created_at,
            al.modified appointment_modified_at,
            /* =========================
            Job Offer (jo)
            ========================= */
            jo.name job_offer_id,
            jo.status job_offer_status,
            jo.offer_date job_offer_date,
            jo.company job_offer_company,
            jo.designation job_offer_designation,
            jo.applicant_email job_offer_applicant_email,
            jo.docstatus job_offer_docstatus,
            jo.creation job_offer_created_at,
            jo.modified job_offer_modified_at
        FROM
            `tabJob Applicant` a
            JOIN `tabJob Opening` j ON a.job_title = j.name
            JOIN `tabJob Pipeline` p ON j.custom_pipeline = p.name
            JOIN `tabPipeline Step` ps ON ps.parent = p.name
            AND a.custom_pipeline_step = ps.name
            LEFT JOIN `tabInterview` i ON i.job_applicant = a.name
            LEFT JOIN `tabInterview Feedback` f ON f.interview = i.name
            LEFT JOIN `tabAppointment Letter` al ON al.job_applicant = a.name
            LEFT JOIN `tabJob Offer` jo ON jo.job_applicant = a.name
    ),
    interviews_agg AS (
        SELECT
            job_opening_id,
            applicant_id,
            interview_id,
            interview_round,
            interview_status,
            interview_scheduled_on,
            interview_from_time,
            interview_to_time,
            interview_expected_avg_rating,
            interview_average_rating,
            interview_job_opening,
            interview_designation,
            interview_docstatus,
            interview_created_at,
            interview_modified_at,
            if(
                feedback_id is null,
                NULL,
                JSON_ARRAYAGG(
                    JSON_OBJECT(
                        'feedback_id',
                        feedback_id,
                        'feedback_interviewer',
                        feedback_interviewer,
                        'feedback_result',
                        feedback_result,
                        'feedback_average_rating',
                        feedback_average_rating,
                        'feedback_text',
                        feedback_text,
                        'feedback_docstatus',
                        feedback_docstatus,
                        'feedback_created_at',
                        feedback_created_at,
                        'feedback_modified_at',
                        feedback_modified_at
                    )
                )
            ) feedbacks
        FROM
            applicants a
        WHERE
            a.interview_id is not null
        GROUP BY
            interview_id,
            interview_round,
            job_opening_id,
            applicant_id,
            interview_status,
            interview_scheduled_on,
            interview_from_time,
            interview_to_time,
            interview_expected_avg_rating,
            interview_average_rating,
            interview_job_opening,
            interview_designation,
            interview_docstatus,
            interview_created_at,
            interview_modified_at
    )
SELECT
    a.job_opening_id,
    a.pipeline_id,
    a.pipeline_description,
    a.pipeline_is_primary,
    a.pipeline_docstatus,
    a.pipeline_created_at,
    a.pipeline_modified_at,
    a.pipeline_step_id,
    a.pipeline_step_idx,
    a.pipeline_step_name,
    a.pipeline_step_type,
    a.pipeline_parent_id,
    a.applicant_id,
    a.applicant_name,
    a.applicant_email,
    a.applicant_phone,
    a.applicant_country,
    a.applicant_job_title,
    a.applicant_designation,
    a.applicant_status,
    a.applicant_source,
    a.applicant_source_name,
    a.applicant_employee_referral,
    a.applicant_rating,
    a.applicant_resume_link,
    a.applicant_resume_attachment,
    a.applicant_cover_letter,
    a.applicant_pipeline_step_ref,
    a.applicant_docstatus,
    a.applicant_created_at,
    a.applicant_modified_at,
    if(
        a.appointment_letter_id is null,
        NULL,
        JSON_ARRAYAGG(
            JSON_OBJECT(
                'appointment_letter_id',
                appointment_letter_id,
                'appointment_company',
                appointment_company,
                'appointment_date',
                appointment_date,
                'appointment_template',
                appointment_template,
                'appointment_docstatus',
                appointment_docstatus,
                'appointment_created_at',
                appointment_created_at,
                'appointment_modified_at',
                appointment_modified_at
            )
        )
    ) appointment_letters,
    if(
        a.job_offer_id is null,
        NULL,
        JSON_ARRAYAGG(
            JSON_OBJECT(
                'job_offer_id',
                job_offer_id,
                'job_offer_status',
                job_offer_status,
                'job_offer_date',
                job_offer_date,
                'job_offer_company',
                job_offer_company,
                'job_offer_designation',
                job_offer_designation,
                'job_offer_applicant_email',
                job_offer_applicant_email,
                'job_offer_docstatus',
                job_offer_docstatus,
                'job_offer_created_at',
                job_offer_created_at,
                'job_offer_modified_at',
                job_offer_modified_at
            )
        )
    ) job_offers,
    IF(
        i.interview_id is null,
        NULL,
        JSON_ARRAYAGG(
            JSON_OBJECT(
                'interview_id',
                i.interview_id,
                'interview_round',
                i.interview_round,
                'interview_status',
                i.interview_status,
                'interview_scheduled_on',
                i.interview_scheduled_on,
                'interview_from_time',
                i.interview_from_time,
                'interview_to_time',
                i.interview_to_time,
                'interview_expected_avg_rating',
                i.interview_expected_avg_rating,
                'interview_average_rating',
                i.interview_average_rating,
                'interview_job_opening',
                i.interview_job_opening,
                'interview_designation',
                i.interview_designation,
                'interview_docstatus',
                i.interview_docstatus,
                'interview_created_at',
                i.interview_created_at,
                'interview_modified_at',
                i.interview_modified_at,
                'feedbacks',
                i.feedbacks
            )
        )
    ) interviews
FROM
    applicants a
    LEFT JOIN interviews_agg i ON a.applicant_id = i.applicant_id
GROUP BY
    a.job_opening_id,
    a.pipeline_id,
    a.pipeline_description,
    a.pipeline_is_primary,
    a.pipeline_docstatus,
    a.pipeline_created_at,
    a.pipeline_modified_at,
    a.pipeline_step_id,
    a.pipeline_step_idx,
    a.pipeline_step_name,
    a.pipeline_step_type,
    a.pipeline_parent_id,
    a.applicant_id,
    a.applicant_name,
    a.applicant_email,
    a.applicant_phone,
    a.applicant_country,
    a.applicant_job_title,
    a.applicant_designation,
    a.applicant_status,
    a.applicant_source,
    a.applicant_source_name,
    a.applicant_employee_referral,
    a.applicant_rating,
    a.applicant_resume_link,
    a.applicant_resume_attachment,
    a.applicant_cover_letter,
    a.applicant_pipeline_step_ref,
    a.applicant_docstatus,
    a.applicant_created_at,
    a.applicant_modified_at;
CREATE OR REPLACE VIEW `tal_job_view` AS
WITH
  -- Step 1: Define the base structure of Jobs and their required Pipeline Steps
  job_structure AS (
    SELECT
      j.name AS job_name,
      j.*, -- Select specific columns in production
      ps.name AS step_id,
      ps.step_name,
      ps.step_type,
      ps.idx AS step_idx
    FROM `tabjob opening` j
    JOIN `tabjob pipeline` p ON j.custom_pipeline = p.name
    JOIN `tabpipeline step` ps ON ps.parent = p.name
  ),

  -- Step 2: Aggregate candidates per step, per job
  step_aggregates AS (
    SELECT
      js.job_name,
      js.step_id,
      js.step_name,
      js.step_type,
      js.step_idx,
      COUNT(a.applicant_id) AS candidate_count,
      JSON_ARRAYAGG(
        IF(a.applicant_id IS NULL, NULL, JSON_OBJECT(
          'applicant_id', a.applicant_id,
          'applicant_name', a.applicant_name,
          'applicant_email', a.applicant_email,
          'applicant_status', a.applicant_status,
          'applicant_rating', a.applicant_rating
          -- Add other applicant fields here without trailing commas
        ))
      ) AS candidates
    FROM job_structure js
    LEFT JOIN `tal_job_applicants_view` a ON (
      js.step_id = a.pipeline_step_id
      AND a.job_opening_id = js.job_name
    )
    GROUP BY js.job_name, js.step_id, js.step_name, js.step_type, js.step_idx
  )

-- Step 3: Final aggregation into Job level
SELECT
  j.name,
  j.designation,
  j.department,
  j.employment_type,
  j.location,
  j.docstatus,
  j.publish_salary_range,
  j.currency,
  j.lower_range,
  j.upper_range,
  j.posted_on,
  j.closes_on,
  COUNT(DISTINCT s.step_id) AS step_count,
  -- Sum the counts from the CTE to avoid duplication across joins
  SUM(s.candidate_count) AS total_candidate_count,
  JSON_ARRAYAGG(
    JSON_OBJECT(
      'step_id', s.step_id,
      'step_name', s.step_name,
      'step_type', s.step_type,
      'step_idx', s.step_idx,
      'candidate_count', s.candidate_count,
      'candidates', s.candidates
    )
  ) AS steps
FROM `tabjob opening` j
LEFT JOIN step_aggregates s ON j.name = s.job_name
GROUP BY
  j.name, j.designation, j.department, j.employment_type,
  j.location, j.docstatus, j.publish_salary_range,
  j.currency, j.lower_range, j.upper_range,
  j.posted_on, j.closes_on;










