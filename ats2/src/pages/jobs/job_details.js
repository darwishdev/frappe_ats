frappe.pages['job-details'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Job Details',
		single_column: true
	});

	
  $(page.main).html(frappe.render_template('job_details', {}));

  // API Client - loaded from apiClient.js
  const API = window.JobDetailsAPI;

  // ---- route options ----
  const opts = frappe.route_options || {};
  frappe.route_options = null;
  const jobId = opts.job || 'JOB-0001';

 // 1) set the module crumb (left-most)
  frappe.breadcrumbs.add('Addicta');

  // 2) If your Frappe has a custom breadcrumb setter, use it
  const crumbs = [
    { label: __('Jobs'), route: '/app/jobs-candidates' },
    { label: __('Job Details') }
  ];

  if (frappe.breadcrumbs.set_custom_breadcrumbs) {
    frappe.breadcrumbs.set_custom_breadcrumbs(crumbs);
  } else if (frappe.breadcrumbs.set_list) {
    frappe.breadcrumbs.set_list(crumbs);
  } else {
    // fallback: only module crumb will show
  }

  // ---- Transform API data ----
  function transformJobData(rawJob) {
    // Extract unique steps
    const stepsMap = new Map();
    const allCandidates = [];
    
    if (rawJob.steps && Array.isArray(rawJob.steps)) {
      rawJob.steps.forEach(step => {
        const stepKey = `${step.step_id}`;
        if (!stepsMap.has(stepKey)) {
          stepsMap.set(stepKey, {
            key: stepKey,
            label: step.step_name,
            id: step.step_id,
            idx: step.step_idx,
            type: step.step_type
          });
        }
        
        // Extract candidates from this step
        if (step.candidates && Array.isArray(step.candidates)) {
          step.candidates.forEach(candidate => {
            // Check if candidate already exists
            const existingIdx = allCandidates.findIndex(c => c.id === candidate['applicant_email,']);
            if (existingIdx === -1) {
              allCandidates.push({
                id: candidate['applicant_email,'],
                name: candidate['applicant_name,'] || 'Unknown',
                email: candidate['applicant_email,'],
                phone: candidate['applicant_phone,'] || 'N/A',
                country: candidate['applicant_country,'] || 'N/A',
                designation: candidate['applicant_designation,'] || rawJob.designation,
                status: candidate['applicant_status,'] || 'Open',
                source: candidate['applicant_source,'] || 'Direct',
                rating: candidate['applicant_rating,'] || 0,
                resume_link: candidate['applicant_resume_link,'],
                cover_letter: candidate['applicant_cover_letter,'],
                stage: stepKey,
                stage_name: step.step_name,
                created_at: candidate['applicant_created_at,'],
                modified_at: candidate['applicant_modified_at,']
              });
            }
          });
        }
      });
    }
    
    const steps = Array.from(stepsMap.values()).sort((a, b) => a.idx - b.idx);
    
    // Add "All" step
    const pipeline_steps = [
      { key: 'all', label: 'All' },
      ...steps
    ];
    
    return {
      name: rawJob.name,
      title: rawJob.designation || 'Untitled Position',
      department: rawJob.department || 'Not Specified',
      location: rawJob.location || 'Not Specified',
      work_mode: rawJob.employment_type || 'Full-time',
      pipeline_steps: pipeline_steps,
      steps: steps,
      candidates: allCandidates
    };
  }

  // Removed: mockFetchJob - now using API.fetchJobDetails from apiClient.js

  // ---- State ----
  let job = null;
  let candidates = [];
  let activeStep = 'all';
  let activeCandidateId = null;
  let selectedCandidates = new Set(); // Track selected candidates for bulk actions

  // ---- Render helpers ----
  const esc = frappe.utils.escape_html;

  function getCountsByStep() {
    const counts = {};
    for (const c of candidates) counts[c.stage] = (counts[c.stage] || 0) + 1;
    counts.all = candidates.length;
    return counts;
  }

  function renderHeader() {
    $('#jd-job-title').text(job.title);
    $('#jd-job-subtitle').text(`${job.department} · ${job.work_mode} · ${job.location}`);

    // Update bulk action button visibility
    const $bulkActions = $('#jd-bulk-actions');
    if (selectedCandidates.size > 0) {
      $bulkActions.show();
      $('#jd-selected-count').text(selectedCandidates.size);
    } else {
      $bulkActions.hide();
    }

    $('#jd-edit-job').off('click').on('click', () => {
      // Route to Job Opening form
      frappe.set_route('Form', 'Job Opening', job.name);
    });

    $('#jd-add-candidate').off('click').on('click', () => {
      // Open dialog to add candidate
      const d = new frappe.ui.Dialog({
        title: __('Add Candidate'),
        fields: [
          { fieldname: 'candidate_name', label: __('Name'), fieldtype: 'Data', reqd: 1 },
          { fieldname: 'candidate_email', label: __('Email'), fieldtype: 'Data', reqd: 1 },
          { fieldname: 'phone', label: __('Phone'), fieldtype: 'Data' },
          { fieldname: 'country', label: __('Country'), fieldtype: 'Link', options: 'Country' },
          { fieldname: 'source', label: __('Source'), fieldtype: 'Select', 
            options: ['Campaign', 'LinkedIn', 'Referral', 'Direct', 'Other'] }
        ],
        primary_action_label: __('Add'),
        primary_action(values) {
          d.hide();
          frappe.show_alert({ message: __('Adding candidate...'), indicator: 'blue' });
          
          API.addCandidate(job.name, values).then(() => {
            frappe.show_alert({ message: __('Candidate added successfully'), indicator: 'green' });
            // Refresh the page data
            init();
          }).catch(err => {
            frappe.msgprint({ title: __('Error'), message: err.message, indicator: 'red' });
          });
        }
      });
      d.show();
    });
  }

  function renderPipeline() {
    const counts = getCountsByStep();

    $('#jd-pipeline').html(
      job.pipeline_steps.map(s => {
        const cnt = counts[s.key] || 0;
        const active = s.key === activeStep ? 'active' : '';
        return `
          <div class="jd-step ${active}" data-step="${esc(s.key)}">
            ${esc(s.label)} <span class="count">${cnt ? cnt : '–'}</span>
          </div>
        `;
      }).join('')
    );
  }

  function filteredCandidates() {
    const q = ($('#jd-search').val() || '').trim().toLowerCase();

    return candidates.filter(c => {
      if (activeStep !== 'all' && c.stage !== activeStep) return false;
      if (q) {
        const hay = `${c.name} ${c.email} ${c.country} ${c.designation} ${c.source}`.toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    });
  }

  function renderCandidateList() {
    const list = filteredCandidates();

    $('#jd-candidate-list').html(
      list.map(c => {
        const appliedAgo = c.created_at ? frappe.datetime.comment_when(c.created_at) : 'Recently';
        const isSelected = selectedCandidates.has(c.id);
        return `
        <div class="jd-item ${c.id === activeCandidateId ? 'active' : ''}" data-candidate="${esc(c.id)}">
          <input type="checkbox" class="jd-candidate-checkbox" data-candidate-id="${esc(c.id)}" ${isSelected ? 'checked' : ''} 
                 onclick="event.stopPropagation();" style="margin-right: 8px;">
          <div class="jd-avatar">${esc(c.name.split(' ').slice(0,1)[0].slice(0,1).toUpperCase())}</div>
          <div>
            <div class="jd-item-name">${esc(c.name)}</div>
            <div class="jd-item-sub">via <b>${esc(c.source)}</b> · ${appliedAgo}</div>
          </div>
        </div>
      `;
      }).join('') || `<div class="text-muted" style="padding:10px;">No candidates</div>`
    );

    // Attach checkbox change handlers
    $('.jd-candidate-checkbox').off('change').on('change', function(e) {
      const candidateId = $(this).attr('data-candidate-id');
      if ($(this).is(':checked')) {
        selectedCandidates.add(candidateId);
      } else {
        selectedCandidates.delete(candidateId);
      }
      renderHeader(); // Update bulk action button
    });
  }

  function renderCandidateDetails() {
    const c = candidates.find(x => x.id === activeCandidateId);
    if (!c) {
      $('#jd-detail-card').html(`<div class="text-muted">Select a candidate from the list.</div>`);
      return;
    }

    // Build step dropdown options
    const stepOptions = job.steps.map(step => 
      `<option value="${esc(step.key)}" ${step.key === c.stage ? 'selected' : ''}>${esc(step.label)}</option>`
    ).join('');

    const ratingStars = '⭐'.repeat(Math.max(0, Math.min(5, c.rating)));
    const appliedAgo = c.created_at ? frappe.datetime.comment_when(c.created_at) : 'Recently';

    $('#jd-detail-card').html(`
      <div class="jd-detail-head" style="display: flex; justify-content: space-between; align-items: center; padding-bottom: 16px; border-bottom: 1px solid var(--border-color, #e6e6e6); margin-bottom: 16px;">
        <div style="display: flex; align-items: center; gap: 12px;">
          <img src="/assets/addicta/images/candidate-icon.png" 
               alt="Candidate" 
               style="width: 48px; height: 48px; border-radius: 50%; object-fit: cover;"
               onerror="this.style.display='none'">
          <div>
            <h3 class="jd-detail-name" style="margin: 0;">${esc(c.name)}</h3>
            <div class="jd-detail-meta">${esc(c.designation || c.email)}</div>
          </div>
        </div>

        <div style="display:flex;flex-direction:column;gap:8px;min-width:200px;">
          <select class="form-control" id="jd-target-step" style="font-size:13px;">
            ${stepOptions}
          </select>
          <button class="btn btn-primary btn-sm" id="jd-move-to-step">Move to selected step</button>
        </div>
      </div>

      <div>
        <div class="jd-badges">
          <span class="jd-badge">📧 ${esc(c.email)}</span>
          <span class="jd-badge">☎ ${esc(c.phone)}</span>
          <span class="jd-badge">🌍 ${esc(c.country)}</span>
        </div>
        <div class="jd-badges" style="margin-top:8px;">
          <span class="jd-badge">Status: ${esc(c.status)}</span>
          <span class="jd-badge">Source: ${esc(c.source)}</span>
          <span class="jd-badge">Rating: ${ratingStars || 'Not rated'}</span>
        </div>
        <div class="jd-badges" style="margin-top:8px;">
          <span class="jd-badge">Current Stage: ${esc(c.stage_name)}</span>
          <span class="jd-badge">Applied: ${appliedAgo}</span>
        </div>
        ${c.cover_letter ? `
          <div style="margin-top:12px;padding:10px;background:#f9fafb;border-radius:6px;">
            <strong>Cover Letter:</strong>
            <p style="margin:4px 0 0 0;color:#6b7280;">${esc(c.cover_letter)}</p>
          </div>
        ` : ''}
        ${c.resume_link ? `
          <div style="margin-top:8px;">
            <a href="${esc(c.resume_link)}" target="_blank" class="btn btn-xs btn-default">📄 View Resume</a>
          </div>
        ` : ''}
        <div style="margin-top:16px;padding-top:16px;border-top:1px solid var(--border-color, #e6e6e6);">
          <button class="btn btn-default btn-sm" id="jd-assign-interview">
            📅 Assign Interview
          </button>
        </div>
      </div>
    `);

    $('#jd-assign-interview').off('click').on('click', () => {
      const interviewDialog = new frappe.ui.Dialog({
        title: __('Assign Interview to {0}', [c.name]),
        fields: [
          {
            fieldname: 'interview_round',
            label: __('Interview Round'),
            fieldtype: 'Select',
            options: [
              'HR Screening',
              'Technical Screening',
              'Technical Interview',
              'Manager Round',
              'Final Round',
              'Cultural Fit'
            ],
            reqd: 1
          },
          {
            fieldname: 'job_applicant',
            label: __('Job Applicant'),
            fieldtype: 'Data',
            default: c.name,
            read_only: 1,
            reqd: 1
          },
          {
            fieldname: 'job_opening',
            label: __('Job Opening'),
            fieldtype: 'Data',
            default: job.title,
            read_only: 1,
            reqd: 1
          },
          {
            fieldname: 'designation',
            label: __('Designation'),
            fieldtype: 'Data',
            default: job.title,
            reqd: 1
          },
          {
            fieldname: 'resume_link',
            label: __('Resume Link'),
            fieldtype: 'Data',
            default: c.resume_link || ''
          },
          {
            fieldname: 'col_break_1',
            fieldtype: 'Column Break'
          },
          {
            fieldname: 'status',
            label: __('Status'),
            fieldtype: 'Select',
            options: [
              'Pending',
              'Scheduled',
              'Completed',
              'Cleared',
              'Rejected',
              'Cancelled'
            ],
            default: 'Scheduled',
            reqd: 1
          },
          {
            fieldname: 'scheduled_on',
            label: __('Scheduled On'),
            fieldtype: 'Date',
            reqd: 1
          },
          {
            fieldname: 'from_time',
            label: __('From Time'),
            fieldtype: 'Time',
            reqd: 1
          },
          {
            fieldname: 'to_time',
            label: __('To Time'),
            fieldtype: 'Time',
            reqd: 1
          },
          {
            fieldname: 'sec_break_1',
            fieldtype: 'Section Break',
            label: __('Additional Details')
          },
          {
            fieldname: 'expected_average_rating',
            label: __('Expected Average Rating'),
            fieldtype: 'Float',
            default: 0,
            description: __('Expected rating out of 5')
          },
          {
            fieldname: '_user_tags',
            label: __('Tags'),
            fieldtype: 'Data',
            description: __('Comma-separated tags (e.g., Urgent,Python)')
          },
          {
            fieldname: 'interview_summary',
            label: __('Interview Summary'),
            fieldtype: 'Small Text',
            description: __('Optional notes or summary')
          }
        ],
        primary_action_label: __('Assign Interview'),
        primary_action(values) {
          // Validate time range
          if (values.from_time && values.to_time && values.from_time >= values.to_time) {
            frappe.msgprint({
              title: __('Invalid Time'),
              message: __('End time must be after start time'),
              indicator: 'red'
            });
            return;
          }

          interviewDialog.hide();
          frappe.show_alert({ message: __('Assigning interview...'), indicator: 'blue' });

          // Prepare interview data
          const interviewData = {
            interview_round: values.interview_round,
            job_applicant: c.email, // Use email as identifier
            job_opening: job.name,
            designation: values.designation,
            resume_link: values.resume_link,
            status: values.status,
            scheduled_on: values.scheduled_on,
            from_time: values.from_time,
            to_time: values.to_time,
            expected_average_rating: values.expected_average_rating || 0,
            _user_tags: values._user_tags || '',
            interview_summary: values.interview_summary || null,
            reminded: 0
          };

          // TODO: Replace with actual API call
          // API.assignInterview(interviewData).then(response => {
          //   frappe.show_alert({
          //     message: __('Interview assigned successfully'),
          //     indicator: 'green'
          //   });
          // }).catch(err => {
          //   frappe.msgprint({
          //     title: __('Error'),
          //     message: err.message || 'Failed to assign interview',
          //     indicator: 'red'
          //   });
          // });

          // Mock success response
          setTimeout(() => {
            frappe.show_alert({
              message: __('Interview assigned to {0} on {1}', [c.name, frappe.datetime.str_to_user(values.scheduled_on)]),
              indicator: 'green'
            });
            console.log('Interview Data:', interviewData);
          }, 500);
        }
      });
      interviewDialog.show();
    });

    $('#jd-move-to-step').off('click').on('click', () => {
      const targetStep = $('#jd-target-step').val();
      const targetStepName = job.steps.find(s => s.key === targetStep)?.label || targetStep;
      
      if (targetStep === c.stage) {
        frappe.show_alert({ message: __('Candidate is already in this stage'), indicator: 'orange' });
        return;
      }
      
      frappe.show_alert({ message: __('Moving candidate...'), indicator: 'blue' });
      
      API.moveCandidateToStep(c.id, job.name, targetStep).then(response => {
        if (response.success) {
          frappe.show_alert({ message: `${c.name} moved to "${targetStepName}"`, indicator: 'green' });
          // Update local state
          c.stage = targetStep;
          c.stage_name = targetStepName;
          renderAll();
        } else {
          frappe.msgprint({ title: __('Error'), message: response.message, indicator: 'red' });
        }
      }).catch(err => {
        frappe.msgprint({ title: __('Error'), message: err.message || 'Failed to move candidate', indicator: 'red' });
      });
    });
  }

  function renderAll() {
    renderHeader();
    renderPipeline();
    renderCandidateList();
    renderCandidateDetails();
  }

  // ---- Events ----
  $(page.main).on('click', '.jd-step', function() {
    activeStep = $(this).attr('data-step');
    selectedCandidates.clear(); // Clear selections when changing steps
    // reset selection if it disappears from filter
    const list = filteredCandidates();
    if (!list.some(x => x.id === activeCandidateId)) activeCandidateId = list[0]?.id || null;
    renderAll();
  });

  $(page.main).on('input', '#jd-search', frappe.utils.debounce(() => {
    const list = filteredCandidates();
    if (!list.some(x => x.id === activeCandidateId)) activeCandidateId = list[0]?.id || null;
    renderCandidateList();
    renderCandidateDetails();
  }, 200));

  $(page.main).on('click', '.jd-item', function() {
    activeCandidateId = $(this).attr('data-candidate');
    renderCandidateList();
    renderCandidateDetails();
  });

  // Bulk actions event handlers
  $(page.main).on('click', '#jd-select-all', function() {
    const list = filteredCandidates();
    if (selectedCandidates.size === list.length) {
      // Deselect all
      selectedCandidates.clear();
    } else {
      // Select all visible candidates
      list.forEach(c => selectedCandidates.add(c.id));
    }
    renderCandidateList();
    renderHeader();
  });

  $(page.main).on('click', '#jd-bulk-move', function() {
    if (selectedCandidates.size === 0) {
      frappe.msgprint(__('Please select candidates first'));
      return;
    }

    // Create dialog for bulk move
    const d = new frappe.ui.Dialog({
      title: __('Bulk Move Candidates'),
      fields: [
        {
          fieldname: 'target_step',
          label: __('Move to Step'),
          fieldtype: 'Select',
          options: job.steps.map(s => s.label).join('\n'),
          reqd: 1
        },
        {
          fieldname: 'status',
          label: __('Update Status'),
          fieldtype: 'Select',
          options: ['', 'Open', 'Hold', 'Rejected', 'Hired'],
          description: __('Optional: Change candidate status')
        },
        {
          fieldname: 'info',
          fieldtype: 'HTML',
          options: `<p class="text-muted">Moving ${selectedCandidates.size} candidate(s)</p>`
        }
      ],
      primary_action_label: __('Move Candidates'),
      primary_action(values) {
        const targetStepLabel = values.target_step;
        const targetStep = job.steps.find(s => s.label === targetStepLabel);
        
        if (!targetStep) {
          frappe.msgprint(__('Invalid step selected'));
          return;
        }

        const payload = {
          names: Array.from(selectedCandidates),
          pipeline_step: targetStep.key
        };

        if (values.status) {
          payload.status = values.status;
        }

        d.hide();
        frappe.show_alert({ message: __('Moving candidates...'), indicator: 'blue' });

        API.bulkUpdateApplicants(payload).then(response => {
          if (response.success) {
            frappe.show_alert({
              message: `${response.updated_count} candidate(s) moved to "${targetStepLabel}"`,
              indicator: 'green'
            });
            
            // Update local state for moved candidates
            selectedCandidates.forEach(candidateId => {
              const candidate = candidates.find(c => c.id === candidateId);
              if (candidate) {
                candidate.stage = targetStep.key;
                candidate.stage_name = targetStep.label;
                if (values.status) {
                  candidate.status = values.status;
                }
              }
            });
            
            // Clear selection and refresh
            selectedCandidates.clear();
            renderAll();
          } else {
            frappe.msgprint({
              title: __('Error'),
              message: response.message || 'Failed to move candidates',
              indicator: 'red'
            });
          }
        }).catch(err => {
          frappe.msgprint({
            title: __('Error'),
            message: err.message || 'Failed to move candidates',
            indicator: 'red'
          });
        });
      }
    });
    d.show();
  });

  $(page.main).on('click', '#jd-clear-selection', function() {
    selectedCandidates.clear();
    renderCandidateList();
    renderHeader();
  });

  // ---- Init ----
  async function init() {
    page.set_indicator(__('Loading...'), 'blue');

    try {
      const rawJob = await API.fetchJobDetails(jobId);
      const transformedData = transformJobData(rawJob);
    
    job = transformedData;
    candidates = transformedData.candidates;

    activeStep = 'all';
    activeCandidateId = candidates[0]?.id || null;

      renderAll();
      page.clear_indicator();
    } catch (err) {
      page.clear_indicator();
      frappe.msgprint({
        title: __('Error Loading Job'),
        message: err.message || 'Failed to load job details',
        indicator: 'red'
      });
    }
  }
  
  // Start initialization
  init();
}
