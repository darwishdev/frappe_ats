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
  },

  

  /**
   * Find job applicant details
   * @param {string} applicantId - Job applicant ID/email
   * @returns {Promise<Object>} Job applicant details (ApplicantResumeDTO)
   */
  jobApplicantFind: function(applicantId) {
    // TODO: Replace with real API call
    // if (!_createResource) {
    //   throw new Error('JobDetailsAPI not initialized. Call JobDetailsAPI.init(createResource) first.');
    // }
    // 
    // const resource = _createResource({
    //   url: 'mawhub.job_applicant_find',
    //   params: {
    //     applicant_id: applicantId
    //   },
    //   auto: true
    // });
    // 
    // return resource.promise;

    // Mock implementation
    return Promise.resolve({
      "job_applicant": "AHMED DARWISH",
      "skills": "Languages & Tools: Go, TypeScript, Node.js, Vue 3, Flutter, Tailwind CSS, HTML/CSS. Databases: PostgreSQL, Supabase, MSSQL, NoSQL. Protocols & APIs: gRPC, REST, GraphQL. Platforms: Supabase (Auth, Storage, Edge Functions), Firebase, Redis. DevOps: Docker, CI/CD, GitHub Actions, DigitalOcean. Architecture: Multi-tenant SaaS, Microservices, CQRS, Clean Architecture",
      "summary": "Versatile and results-driven platform architect with 7+ years of experience designing and building scalable backend systems, developer tooling, and BaaS-powered platforms. Specialized in cloud-native architectures, multi-tenant SaaS, and Supabase-backed systems. Contributor to the open-source community, particularly in Supabase (Auth and Storage Go clients) and PrimeVue, with a passion for creating maintainable ecosystems and developer-first tooling. Experienced in delivering robust backend services using Go, PostgreSQL, gRPC, and TypeScript.",
      "education": [
        {
          "degree": "Bachelor of Science in Information Systems",
          "institution": "Future Academy",
          "from_date": "2014-09-01",
          "to_date": "2018-06-01"
        }
      ],
      "experience": [
        {
          "company": "ABC Hotels, Egypt",
          "role": "Senior Platform Engineer",
          "from_date": "2024-01-01",
          "to_date": null,
          "description": "● Architected and led the development of Yalabina, a multi-tenant hotel reservation platform used by over 20 hotel properties.\n● Designed the backend architecture using Go, gRPC, PostgreSQL, and Supabase Auth/Storage, with modular services and tenant isolation.\n● Built a full-stack platform with Vue 3 and Tailwind CSS, including content CMS, booking engine, pricing rules, and admin dashboards.\n● Automated provisioning of new hotel tenants through Devkit CLI, reducing setup time from 3 days to under 1 hour.\n● Integrated Salesforce and payment gateways (Stripe, Paymob), increasing booking conversion rates by 15%.\n● Delivered 99.99% uptime across staging and production using containerized deployments and CI/CD pipelines.\n● Created reusable mocks and test harnesses to support local and automated testing across gRPC endpoints."
        },
        {
          "company": "Melon, Egypt",
          "role": "Lead Full Stack Developer",
          "from_date": "2021-01-01",
          "to_date": "2023-12-31",
          "description": "● Led a team of 5 engineers in the development of a restaurant management suite (POS, KDS, Waiter App, Digital Menu) deployed in over 30 venues.\n● Built real-time, offline-first sync system using WebRTC and Vue.js, ensuring data availability in disconnected branches.\n● Developed the full client suite:\n○ Web Admin Dashboard and POS with role-based access\n○ Flutter Android App with printer support\n○ Web-based Digital Menu for customer ordering\n○ KDS (Kitchen Display System) for kitchen operations\n● Created the open-source v-dashkit Vue component library for admin CRUD UIs, reducing dashboard development time by ~30%.\n● Deployed CI/CD pipelines with preview environments, GitHub Actions, and branch-based testing."
        },
        {
          "company": "Business Pro, Remote (USA)",
          "role": "Full Stack Developer",
          "from_date": "2019-01-01",
          "to_date": "2022-12-31",
          "description": "● Developed Alshab Alriyadi, a platform connecting entrepreneurs and investors, with over 5,000 monthly active users.\n● Designed and implemented scalable microservices using Node.js and PostgreSQL, improving response times by 25%.\n● Added real-time chat and search features, increasing user engagement and match success rates by 30%.\n● Collaborated with remote product and design teams, reducing release cycles by 20%."
        },
        {
          "company": "Elnozom, Egypt",
          "role": "Web Developer",
          "from_date": "2018-01-01",
          "to_date": "2020-12-31",
          "description": "● Modernized legacy ERP systems (15+ branches) by integrating web portals with MSSQL and migrating to cloud infrastructure.\n● Built PDA applications for field sales and inventory, increasing on-site data accuracy by 25%.\n● Designed a DNS automation system for seamless remote access to on-prem databases, reducing IT support overhead by 35%.\n● Reduced infrastructure cost by 15% through phased cloud migration and streamlined configuration."
        }
      ],
      "projects": [
        {
          "title": "Devkit CLI",
          "description": "Monorepo CLI tool for platform automation. Automates full-stack Supabase-based project scaffolding, including Auth, SQL, and Storage. Enables rapid bootstrapping of tenants with seeded users, files, and permissions. Core tool for onboarding and DevOps operations at ABC Hotels and internal tools. Fully scriptable and integrated into CI/CD pipelines.",
          "link": "https://github.com/darwishdev/devkit-cli"
        },
        {
          "title": "Devkit API",
          "description": "Modular gRPC backend framework. Designed with Clean Architecture principles. Implements CQRS, Redis caching, request tracing, and multi-tenant isolation. Powers the core backend for Yalabina and other internal tools. Provides centralized access to Supabase services, audit logs, and session control.",
          "link": "https://github.com/darwishdev/devkit-api"
        },
        {
          "title": "SQLSeeder",
          "description": "Declarative PostgreSQL data seeding tool. Allows seeding complex relational data from Excel and JSON into Supabase-hosted or standard PostgreSQL databases. Supports environment-specific branching, migration safety, and structured relationship resolution. Used across dev/staging/test environments and integrated with Devkit CLI for onboarding workflows. Open sourced for community use.",
          "link": "https://github.com/darwishdev/sqlseeder"
        },
        {
          "title": "Yalabina",
          "description": "Hotel reservation and content platform (owned by ABC Hotels). Multi-tenant platform enabling booking, property management, and guest CMS operations across 20+ hotels. Built with Supabase (Auth, Storage, Functions), Go (API), and Vue 3 (UI). Integrated dynamic pricing, availability sync, and multi-user role management with real-time updates. Achieved a 40% reduction in operational overhead through full automation and unified infrastructure.",
          "link": "https://yalabina.com"
        }
      ],
      "links": [
        {
          "label": "GitHub",
          "url": "https://github.com/darwishdev"
        },
        {
          "label": "Email",
          "url": "mailto:a.darwish.dev@gmail.com"
        },
        {
          "label": "Phone",
          "url": "tel:+201022052546"
        }
      ]
    });
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
  }
};

// Keep window.JobDetailsAPI for backward compatibility
if (typeof window !== 'undefined') {
  window.JobDetailsAPI = JobDetailsAPI;
}

export default JobDetailsAPI;
