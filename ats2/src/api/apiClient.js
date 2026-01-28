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
   * Create or update a job applicant
   * @param {Object} applicantData - Job applicant information
   * @returns {Promise<Object>} Created/updated applicant details
   */
  createOrUpdateApplicant: function(applicantData) {
    if (!_createResource) {
      throw new Error('JobDetailsAPI not initialized. Call JobDetailsAPI.init(createResource) first.');
    }
    
    const resource = _createResource({
      url: 'mawhub.job_applicant_create_update',
      params: {
        payload: applicantData
      },
      auto: true
    });
    
    return resource.promise;
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
  },

  

  /**
   * Find job applicant details
   * @param {string} applicantId - Job applicant ID/email
   * @returns {Promise<Object>} Job applicant details (ApplicantResumeDTO)
   */
  jobApplicantFind: function(applicantId) {
    if (!_createResource) {
      throw new Error('JobDetailsAPI not initialized. Call JobDetailsAPI.init(createResource) first.');
    }
    
    const resource = _createResource({
      url: 'mawhub.job_applicant_find',
      method : 'GET',
      params: {
        name: applicantId
      },
      auto: true
    });
    
    return resource.promise;
  },

  /**
   * Create or update an interview
   * @param {Object} interviewData - Interview information
   * @param {string} interviewData.job_applicant - Job applicant ID/email
   * @param {string} interviewData.interview_round - Interview round name
   * @param {string} interviewData.status - Interview status
   * @param {string} interviewData.scheduled_on - Scheduled date (YYYY-MM-DD)
   * @param {string} interviewData.from_time - Start time (HH:MM:SS)
   * @param {string} interviewData.to_time - End time (HH:MM:SS)
   * @param {number} interviewData.expected_average_rating - Expected rating (0-5)
   * @param {string} interviewData.interview_summary - Interview notes/summary
   * @returns {Promise<Object>} Created/updated interview details
   */
  createOrUpdateInterview: function(interviewData) {
    if (!_createResource) {
      throw new Error('JobDetailsAPI not initialized. Call JobDetailsAPI.init(createResource) first.');
    }
    
    const resource = _createResource({
      url: 'mawhub.interview_create_update',
      params: {
        payload : interviewData 
      },
      auto: true
    });
    
    return resource.promise;
  },

  /**
   * Parse resume and create job applicant (EventStream)
   * @param {Object} resumeData - Resume parsing data
   * @param {string} resumeData.file_url - Uploaded resume file URL
   * @param {string} resumeData.file_name - Resume file name
   * @param {string} resumeData.job_opening - Job Opening ID
   * @param {Function} onProgress - Optional callback for progress updates (step, data)
   * @returns {Promise<Object>} Final parsed resume data and created applicant
   */
  parseResume: async function(resumeData, onProgress = null) {
    return new Promise(async (resolve, reject) => {
      // Build query parameters
      const params = new URLSearchParams({
        ...resumeData,
      });
      
      // Construct the URL (adjust base URL as needed)
      const url = `/api/method/mawhub.applicant_resume_parse?${params.toString()}`;
      
      // Create EventSource for SSE
      const eventSource = new EventSource(url, { withCredentials: true });
      let finalResult = null;
      
      eventSource.onmessage = (event) => {
        try {
          if(!event.data) return;
          const data = JSON.parse(event.data);
          console.log(data);
          
          // Call progress callback if provided
          if (onProgress && typeof onProgress === 'function') {
            onProgress(data);
          }
          
          // Store the last message as the final result
          finalResult = data;
          
          console.log('Resume parsing progress:', data);
        } catch (error) {
          console.error('Failed to parse SSE message:', error, event.data);
        }
      };
      
      eventSource.onerror = (error) => {
        // console.error('EventSource error:', error);
        eventSource.close();
        
        // If we have a final result, consider it success
        if (finalResult) {
          resolve(finalResult);
        } else {
          reject(new Error('Resume parsing failed: Connection error'));
        }
      };
      
      // Handle completion (if server sends a specific event)
      eventSource.addEventListener('complete', (event) => {
        try {
          const data = JSON.parse(event.data);
          eventSource.close();
          resolve(data);
        } catch (error) {
          eventSource.close();
          reject(new Error('Failed to parse completion message'));
        }
      });
      
      // Fallback: close connection after timeout
      setTimeout(() => {
        if (eventSource.readyState !== EventSource.CLOSED) {
          eventSource.close();
          if (finalResult) {
            resolve(finalResult);
          } else {
            reject(new Error('Resume parsing timed out'));
          }
        }
      }, 90000); // 90 second timeout

    });
  },

  /**
   * Send email to job applicant
   * @param {Object} emailData - Email data
   * @param {string} emailData.recipient - Recipient email address
   * @param {string} emailData.subject - Email subject
   * @param {string} emailData.message - Email message/body
   * @param {string} emailData.cc - CC emails (comma separated)
   * @param {string} emailData.bcc - BCC emails (comma separated)
   * @param {boolean} emailData.send_me_a_copy - Send copy to sender
   * @param {string} emailData.job_applicant - Job applicant ID
   * @param {string} emailData.job_opening - Job opening ID
   * @returns {Promise<Object>} Email send result
   */
  sendEmail: function(emailData) {
    if (!_createResource) {
      throw new Error('JobDetailsAPI not initialized. Call JobDetailsAPI.init(createResource) first.');
    }
    
    const resource = _createResource({
      url: 'mawhub.send_applicant_email',
      params: {
        payload: emailData
      },
      auto: true
    });
    
    return resource.promise;
  },

  /**
   * Parse job opening from document (EventStream)
   * @param {Object} jobData - Job parsing data
   * @param {string} jobData.path - Uploaded document file URL
   * @param {string} jobData.file_name - Document file name
   * @param {Function} onProgress - Optional callback for progress updates
   * @returns {Promise<Object>} Final parsed job data
   */
  parseJobOpening: async function(jobData, onProgress = null) {
    return new Promise(async (resolve, reject) => {
      // Build query parameters
      const params = new URLSearchParams({
        ...jobData,
      });
      
      // Construct the URL
      const url = `/api/method/mawhub.job_opening_parse?${params.toString()}`;
      
      // Create EventSource for SSE
      const eventSource = new EventSource(url, { withCredentials: true });
      let finalResult = null;
      
      eventSource.onmessage = (event) => {
        try {
          if(!event.data) return;
          const data = JSON.parse(event.data);
          console.log(data);
          
          // Call progress callback if provided
          if (onProgress && typeof onProgress === 'function') {
            onProgress(data);
          }
          
          // Store the last message as the final result
          finalResult = data;
          
          console.log('Job parsing progress:', data);
        } catch (error) {
          console.error('Failed to parse SSE message:', error, event.data);
        }
      };
      
      eventSource.onerror = (error) => {
        eventSource.close();
        
        // If we have a final result, consider it success
        if (finalResult) {
          resolve(finalResult);
        } else {
          reject(new Error('Job parsing failed: Connection error'));
        }
      };
      
      // Handle completion event
      eventSource.addEventListener('complete', (event) => {
        try {
          const data = JSON.parse(event.data);
          eventSource.close();
          resolve(data);
        } catch (error) {
          eventSource.close();
          reject(new Error('Failed to parse completion message'));
        }
      });
      
      // Fallback: close connection after timeout
      setTimeout(() => {
        if (eventSource.readyState !== EventSource.CLOSED) {
          eventSource.close();
          if (finalResult) {
            resolve(finalResult);
          } else {
            reject(new Error('Job parsing timed out'));
          }
        }
      }, 90000); // 90 second timeout

    });
  },

  /**
   * Generate email content using AI
   * @param {Object} emailConfig - Email generation configuration
   * @param {string} emailConfig.candidate_name - Candidate's name
   * @param {string} emailConfig.candidate_email - Candidate's email
   * @param {string} emailConfig.job_title - Job title
   * @param {string} emailConfig.custom_prompt - Optional custom instructions for AI
   * @returns {Promise<Object>} Generated email content
   */
  generateEmail: function(emailConfig) {
    if (!_createResource) {
      throw new Error('JobDetailsAPI not initialized. Call JobDetailsAPI.init(createResource) first.');
    }
    
    const resource = _createResource({
      url: 'mawhub.generate_applicant_email',
      params: {
        payload: emailConfig
      },
      auto: true
    });
    
    return resource.promise;
  },

  /**
   * Save email template for future use
   * @param {Object} templateConfig - Template configuration
   * @param {string} templateConfig.template_name - Template name
   * @param {string} templateConfig.description - Template description
   * @param {string} templateConfig.subject - Email subject template
   * @param {string} templateConfig.message - Email message template
   * @returns {Promise<Object>} Saved template details
   */
  saveEmailTemplate: function(templateConfig) {
    if (!_createResource) {
      throw new Error('JobDetailsAPI not initialized. Call JobDetailsAPI.init(createResource) first.');
    }
    
    const resource = _createResource({
      url: 'mawhub.save_email_template',
      params: {
        payload: templateConfig
      },
      auto: true
    });
    
    return resource.promise;
  },

  /**
   * Find job opening details
   * @param {string} jobName - Job opening name/ID
   * @returns {Promise<Object>} Job opening details
   */
  findJobOpening: function(jobName) {
    if (!_createResource) {
      throw new Error('JobDetailsAPI not initialized. Call JobDetailsAPI.init(createResource) first.');
    }
    
    const resource = _createResource({
      url: 'mawhub.job_opening_find',
      method: 'GET',
      params: {
        job: jobName
      },
      auto: true
    });
    
    return resource.promise;
  },

  /**
   * Create or update a job opening
   * @param {Object} jobData - Job opening data
   * @param {string} jobData.name - Job opening name/ID (for updates)
   * @param {number} jobData.vacancies - Number of vacancies
   * @param {string} jobData.job_title - Job title
   * @param {string} jobData.status - Job status (Open, Closed, On Hold)
   * @param {string} jobData.description - Job description
   * @param {string} jobData.department - Department
   * @param {string} jobData.employment_type - Employment type (Full-time, Part-time, etc.)
   * @param {string} jobData.location - Location
   * @param {string} jobData.staffing_plan - Staffing plan
   * @param {number} jobData.planned_vacancies - Planned vacancies
   * @param {number} jobData.publish - Publish status (0 or 1)
   * @param {number} jobData.publish_applications_received - Publish applications received (0 or 1)
   * @param {string} jobData.currency - Currency code
   * @param {number} jobData.lower_range - Lower salary range
   * @param {number} jobData.upper_range - Upper salary range
   * @param {string} jobData.salary_per - Salary period (Month, Year, Hour)
   * @param {number} jobData.publish_salary_range - Publish salary range (0 or 1)
   * @param {string} jobData.custom_pipeline - Custom pipeline name
   * @returns {Promise<Object>} Created/updated job opening details
   */
  createOrUpdateJobOpening: function(jobData) {
    if (!_createResource) {
      throw new Error('JobDetailsAPI not initialized. Call JobDetailsAPI.init(createResource) first.');
    }
    
    const resource = _createResource({
      url: 'mawhub.job_opening_create_update',
      params: {
        payload: jobData
      },
      auto: true
    });
    
    return resource.promise;
  },

  /**
   * Create or update a parsed document
   * @param {Object} parsedDocData - Parsed document data
   * @param {string} parsedDocData.file - File path
   * @param {string} parsedDocData.file_hash - File hash
   * @param {string} parsedDocData.parent_type - Parent type (Job Opening, Job Application, etc.)
   * @param {string} parsedDocData.parent_id - Parent ID
   * @param {Array} parsedDocData.sections - Sections array with title, description, and pullet_points
   * @returns {Promise<Object>} Created/updated parsed document details
   */
  createOrUpdateParsedDocument: function(parsedDocData) {
    if (!_createResource) {
      throw new Error('JobDetailsAPI not initialized. Call JobDetailsAPI.init(createResource) first.');
    }
    
    const resource = _createResource({
      url: 'mawhub.parsed_document_create_update',
      params: {
        payload: parsedDocData
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
