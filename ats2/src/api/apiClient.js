/**
 * API Client for Job Details
 * 
 * Replace mock implementations with real API calls when backend is ready.
 * All API methods return Promises.
 */

let _createResource = null;

export const JobDetailsAPI = {
  /**
   * Initialize the API client with frappe-ui createResource function
   * Call this in onMounted of your Vue component
   * @param {Function} createResource - createResource function from frappe-ui
   */
  init: function(createResource) {
    _createResource = createResource;
  },
  /**
   * Fetch job details with all pipeline steps and candidates
   * @param {string} jobId - Job Opening ID
   * @returns {Promise<Object>} Job details with steps and candidates
   */
  fetchJobDetails: function(jobId) {
    // TODO: Replace with real API call
    // return frappe.call({
    //   method: 'addicta.api.get_job_details',
    //   args: { job_id: jobId }
    // }).then(r => r.message);

    // Mock implementation
    return Promise.resolve({
    "name": "HR-OPN-2026-0002",
    "designation": "Engineer",
    "department": null,
    "employment_type": "Part-time",
    "location": "Remote",
    "docstatus": 0,
    "publish_salary_range": 0,
    "publish_applications_received": 1,
    "publish": 1,
    "route": "jobs/mawhub/senior-be",
    "job_application_route": null,
    "currency": "EGP",
    "salary_per": "Month",
    "lower_range": "0",
    "upper_range": "0",
    "posted_on": "2026-01-15 14:03:09.000000",
    "closes_on": "2026-01-31",
    "step_count": "5",
    "candidate_count": "3",
    "steps": [
      {
        "step_id": 1,
        "step_name": "Applied",
        "step_type": "screening",
        "step_idx": 1,
        "candidates": [
          {
            "job_opening_id,": "HR-OPN-2026-0002",
            "pipeline_id,": "Main",
            "pipeline_description,": null,
            "pipeline_is_primary,": 1,
            "pipeline_docstatus,": 0,
            "pipeline_created_at,": "2026-01-15 13:53:40.805874",
            "pipeline_modified_at,": "2026-01-15 13:53:40.805874",
            "pipeline_step_id,": 1,
            "pipeline_step_idx,": 1,
            "pipeline_step_name,": "Applied",
            "pipeline_step_type,": "screening",
            "pipeline_parent_id,": "Main",
            "applicant_id,": "m.m@gmail.com",
            "applicant_name,": "mohamed",
            "applicant_email,": "m.m@gmail.com",
            "applicant_phone,": null,
            "applicant_country,": "Egypt",
            "applicant_job_title,": "HR-OPN-2026-0002",
            "applicant_designation,": "Engineer",
            "applicant_status,": "Open",
            "applicant_source,": "Campaign",
            "applicant_source_name,": null,
            "applicant_employee_referral,": null,
            "applicant_rating,": 0,
            "applicant_resume_link,": null,
            "applicant_resume_attachment,": null,
            "applicant_cover_letter,": null,
            "applicant_pipeline_step_ref,": "1",
            "applicant_docstatus,": 0,
            "applicant_created_at,": "2026-01-15 14:05:36.548142",
            "applicant_modified_at,": "2026-01-15 14:14:01.488181",
            "appointment_letters,": null,
            "job_offers,": null,
            "interviews,": null
          },
          {
            "job_opening_id,": "HR-OPN-2026-0002",
            "pipeline_id,": "Main",
            "pipeline_description,": null,
            "pipeline_is_primary,": 1,
            "pipeline_docstatus,": 0,
            "pipeline_created_at,": "2026-01-15 13:53:40.805874",
            "pipeline_modified_at,": "2026-01-15 13:53:40.805874",
            "pipeline_step_id,": 1,
            "pipeline_step_idx,": 1,
            "pipeline_step_name,": "Applied",
            "pipeline_step_type,": "screening",
            "pipeline_parent_id,": "Main",
            "applicant_id,": "new@gmail.com",
            "applicant_name,": "new applicant",
            "applicant_email,": "new@gmail.com",
            "applicant_phone,": "",
            "applicant_country,": "Egypt",
            "applicant_job_title,": "HR-OPN-2026-0002",
            "applicant_designation,": "Engineer",
            "applicant_status,": "Open",
            "applicant_source,": null,
            "applicant_source_name,": null,
            "applicant_employee_referral,": null,
            "applicant_rating,": 0,
            "applicant_resume_link,": "",
            "applicant_resume_attachment,": null,
            "applicant_cover_letter,": "",
            "applicant_pipeline_step_ref,": "1",
            "applicant_docstatus,": 0,
            "applicant_created_at,": "2026-01-15 14:45:56.137779",
            "applicant_modified_at,": "2026-01-16 14:52:41.574633",
            "appointment_letters,": null,
            "job_offers,": null,
            "interviews,": null
          }
        ],
        "candidate_count": 2
      },
      {
        "step_id": 2,
        "step_name": "HR Screening",
        "step_type": "screening",
        "step_idx": 2,
        "candidates": [],
        "candidate_count": 0
      },
      {
        "step_id": 3,
        "step_name": "Technical Interview",
        "step_type": "interview",
        "step_idx": 3,
        "candidates": [
          {
            "job_opening_id,": "HR-OPN-2026-0002",
            "pipeline_id,": "Main",
            "pipeline_description,": null,
            "pipeline_is_primary,": 1,
            "pipeline_docstatus,": 0,
            "pipeline_created_at,": "2026-01-15 13:53:40.805874",
            "pipeline_modified_at,": "2026-01-15 13:53:40.805874",
            "pipeline_step_id,": 3,
            "pipeline_step_idx,": 3,
            "pipeline_step_name,": "Technical Interview",
            "pipeline_step_type,": "interview",
            "pipeline_parent_id,": "Main",
            "applicant_id,": "ahmed@test.com",
            "applicant_name,": "ahmed",
            "applicant_email,": "ahmed@test.com",
            "applicant_phone,": "+201234567890",
            "applicant_country,": "Egypt",
            "applicant_job_title,": "HR-OPN-2026-0002",
            "applicant_designation,": "Engineer",
            "applicant_status,": "Open",
            "applicant_source,": "LinkedIn",
            "applicant_source_name,": null,
            "applicant_employee_referral,": null,
            "applicant_rating,": 4,
            "applicant_resume_link,": null,
            "applicant_resume_attachment,": null,
            "applicant_cover_letter,": "I am very interested in this position",
            "applicant_pipeline_step_ref,": "3",
            "applicant_docstatus,": 0,
            "applicant_created_at,": "2026-01-10 14:05:36.548142",
            "applicant_modified_at,": "2026-01-16 14:14:01.488181",
            "appointment_letters,": null,
            "job_offers,": null,
            "interviews,": null
          }
        ],
        "candidate_count": 1
      },
      {
        "step_id": 4,
        "step_name": "Offer",
        "step_type": "offer",
        "step_idx": 4,
        "candidates": [],
        "candidate_count": 0
      },
      {
        "step_id": 5,
        "step_name": "Hired",
        "step_type": "hired",
        "step_idx": 5,
        "candidates": [],
        "candidate_count": 0
      }
    ]
  });
},

  /**
   * Move a candidate to a different pipeline step
   * @param {string} candidateId - Candidate email/ID
   * @param {string} jobId - Job Opening ID
   * @param {string} targetStep - Target step ID
   * @returns {Promise<Object>} Result of the move operation
   */
  moveCandidateToStep: function(candidateId, jobId, targetStep) {
  // TODO: Replace with real API call
  // return frappe.call({
  //   method: 'addicta.api.move_candidate',
  //   args: {
  //     candidate_id: candidateId,
  //     job_id: jobId,
  //     target_step: targetStep
  //   }
  // }).then(r => r.message);

  // Mock implementation
  return Promise.resolve({
    success: true,
    message: 'Candidate moved successfully',
    candidate_id: candidateId,
    new_stage: targetStep
  });
},

  /**
   * Add a new candidate to the job opening
   * @param {string} jobId - Job Opening ID
   * @param {Object} candidateData - Candidate information
   * @returns {Promise<Object>} Created candidate details
   */
  addCandidate: function(jobId, candidateData) {
  // TODO: Replace with real API call
  // return frappe.call({
  //   method: 'addicta.api.add_candidate',
  //   args: {
  //     job_id: jobId,
  //     candidate: candidateData
  //   }
  // }).then(r => r.message);

  // Mock implementation
  return Promise.resolve({
    success: true,
    message: 'Candidate added successfully',
    candidate_id: candidateData.email
  });
},

  /**
   * Update candidate rating
   * @param {string} candidateId - Candidate email/ID
   * @param {string} jobId - Job Opening ID
   * @param {number} rating - Rating value (0-5)
   * @returns {Promise<Object>} Update result
   */
  updateCandidateRating: function(candidateId, jobId, rating) {
  // TODO: Replace with real API call
  // return frappe.call({
  //   method: 'addicta.api.update_candidate_rating',
  //   args: {
  //     candidate_id: candidateId,
  //     job_id: jobId,
  //     rating: rating
  //   }
  // }).then(r => r.message);

  // Mock implementation
  return Promise.resolve({
    success: true,
    message: 'Rating updated successfully',
    new_rating: rating
  });
},

  /**
   * Update candidate status
   * @param {string} candidateId - Candidate email/ID
   * @param {string} jobId - Job Opening ID
   * @param {string} status - New status (Open, Closed, Rejected, Hired)
   * @returns {Promise<Object>} Update result
   */
  updateCandidateStatus: function(candidateId, jobId, status) {
  // TODO: Replace with real API call
  // return frappe.call({
  //   method: 'addicta.api.update_candidate_status',
  //   args: {
  //     candidate_id: candidateId,
  //     job_id: jobId,
  //     status: status
  //   }
  // }).then(r => r.message);

  // Mock implementation
  return Promise.resolve({
    success: true,
    message: 'Status updated successfully',
    new_status: status
  });
},

  /**
   * Search/filter candidates
   * @param {string} jobId - Job Opening ID
   * @param {Object} filters - Search filters
   * @returns {Promise<Array>} Filtered candidates
   */
  searchCandidates: function(jobId, filters) {
  // TODO: Replace with real API call
  // return frappe.call({
  //   method: 'addicta.api.search_candidates',
  //   args: {
  //     job_id: jobId,
  //     query: filters.query,
  //     stage: filters.stage,
  //     limit: filters.limit || 50
  //   }
  // }).then(r => r.message);

  // Mock implementation - returns empty for now
  return Promise.resolve([]);
  },

  /**
   * Bulk update applicants - move multiple candidates to a step and/or update status
   * @param {Object} payload - Bulk update data
   * @param {Array<string>} payload.names - Array of candidate IDs/emails
   * @param {string} payload.status - New status (Open, Hold, Rejected, etc.)
   * @param {string} payload.pipeline_step - Target pipeline step ID
   * @returns {Promise<Object>} Bulk update result
   */
  bulkUpdateApplicants: function(payload) {
    if (!_createResource) {
      throw new Error('JobDetailsAPI not initialized. Call JobDetailsAPI.init(createResource) first.');
    }
    
    const resource = _createResource({
      url: 'mawhub.job_applicant_bulk_update',
      params: {
        payload: payload
      },
      auto: true
    });
    
    return resource.promise;
  }
};

// Keep window.JobDetailsAPI for backward compatibility
if (typeof window !== 'undefined') {
  window.JobDetailsAPI = JobDetailsAPI;
}

export default JobDetailsAPI;
