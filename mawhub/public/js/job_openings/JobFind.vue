<script setup>
import { ref, computed, onMounted, getCurrentInstance, h, render } from "vue";
import JobDescriptionContent from "./components/JobDescriptionContent.vue";
import ApplicantProfile from "./components/ApplicantProfile.vue";
import ApplicantTimeline from "./components/ApplicantTimeline.vue";
import ApplicantCommunication from "./components/ApplicantCommunication.vue";
import ApplicantReview from "./components/ApplicantReview.vue";
import ApplicantComments from "./components/ApplicantComments.vue";
import ApplicantResume from "./components/ApplicantResume.vue";

// Access frappe instance
const { proxy } = getCurrentInstance();
const frappe = proxy.$frappe;
const frm = proxy.$frm;
console.log(frm);

// State
const job = ref(null);
const steps = ref([]);
const activeStep = ref(null);
const activeCandidateId = ref(null);
const selectedCandidates = ref(new Set());
const searchQuery = ref("");
const loading = ref(false);
const activeTab = ref("profile");

// Get job ID and optional step code from route/query
const route = frappe.get_route();
const jobId = ref(route[2]);
// Get step from query parameter if provided
const initialStepCode = ref(frappe.utils.get_url_arg('step') || null);

// Tab configuration
const tabs = [
  { key: "profile", label: "Profile" },
  { key: "resume", label: "Resume" },
  { key: "timeline", label: "Timeline" },
  { key: "communication", label: "Communication" },
  // { key: "review", label: "Review" },
  { key: "comments", label: "Comments" },
];

const tabComponents = {
  profile: ApplicantProfile,
  resume: ApplicantResume,
  timeline: ApplicantTimeline,
  communication: ApplicantCommunication,
  review: ApplicantReview,
  comments: ApplicantComments,
};

// Computed
const stepOptions = computed(() => {
  if (!job.value?.steps) return [];
  return job.value.steps.map((step) => ({
    label: step.step_name,
    value: step.step_code,
  }));
});

const filteredCandidates = computed(() => {
  if (!job.value?.steps_map || !activeStep.value) return [];

  const candidates = job.value.steps_map[activeStep.value] || [];
  if (!candidates.length) return [];

  if (!searchQuery.value) {
    return candidates;
  }

  const query = searchQuery.value.toLowerCase();
  return candidates.filter((c) =>
    c.job_applicant?.toLowerCase().includes(query) ||
    c.applicant_email?.toLowerCase().includes(query)
  );
});

const activeCandidate = computed(() => {
  if (!activeCandidateId.value) return null;
  return filteredCandidates.value.find(
    (c) => c.name === activeCandidateId.value
  ) || null;
});

const allSelected = computed(() => {
  const filtered = filteredCandidates.value;
  return filtered.length > 0 && selectedCandidates.value.size === filtered.length;
});
console.log(frm);

// Methods
const getJobOpening = async () => {
  loading.value = true;

  try {
    const result = await frm.call("fetch_job_info", {
      job: jobId.value,
      name: jobId.value
    });

    console.log("Server response:", result);

    if (result.message) {
      job.value = result.message;

      // Populate steps directly from the steps array
      setPipelineSteps(result.message.steps);

      frappe.show_alert({
        message: "Job details loaded successfully",
        indicator: "green"
      });
    }
  } catch (error) {
    console.error(error);
    frappe.msgprint({
      title: "Error",
      message: "Failed to load job details",
      indicator: "red"
    });
  } finally {
    loading.value = false;
  }
};

const setPipelineSteps = (stepsData) => {
  steps.value = stepsData;

  // Set active step: prioritize route parameter, fallback to first step
  if (!activeStep.value && steps.value.length > 0) {
    if (initialStepCode.value) {
      // Check if the step code from route exists in the steps
      const stepExists = steps.value.some(step => step.step_code === initialStepCode.value);
      activeStep.value = stepExists ? initialStepCode.value : steps.value[0].step_code;
    } else {
      activeStep.value = steps.value[0].step_code;
    }
  }

  // Set first candidate as active if available (candidates are in steps_map)
  const candidates = job.value?.steps_map?.[activeStep.value] || [];
  if (candidates.length > 0) {
    activeCandidateId.value = candidates[0].name;
  }
};

const changeStep = (stepKey) => {
  activeStep.value = stepKey;
  selectedCandidates.value.clear();

  const filtered = filteredCandidates.value;
  const currentCandidateExists = filtered.some(
    (c) => c.name === activeCandidateId.value
  );

  if (!currentCandidateExists) {
    activeCandidateId.value = filtered[0]?.name || null;
  }
};

const selectCandidate = (candidateId) => {
  activeCandidateId.value = candidateId;
};

const toggleCandidateSelection = (candidateId) => {
  if (selectedCandidates.value.has(candidateId)) {
    selectedCandidates.value.delete(candidateId);
  } else {
    selectedCandidates.value.add(candidateId);
  }
};

const toggleSelectAll = () => {
  if (allSelected.value) {
    selectedCandidates.value.clear();
  } else {
    filteredCandidates.value.forEach((c) => {
      selectedCandidates.value.add(c.name);
    });
  }
};

const clearSelection = () => {
  selectedCandidates.value.clear();
};

// Transform parsed documents for display
const transformedParsedData = computed(() => {
  if (!job.value?.parsed_documents || job.value.parsed_documents.length === 0) {
    return {};
  }
  const parsedDoc = job.value.parsed_documents[0];
  const transformed = {};

  if (parsedDoc.sections && Array.isArray(parsedDoc.sections)) {
    parsedDoc.sections.forEach((section) => {
      const key = section.title
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, "_")
        .replace(/^_+|_+$/g, "");

      let bulletPoints = [];
      if (section.bullet_points) {
        // Handle newline-delimited string format
        if (typeof section.bullet_points === "string") {
          let text = section.bullet_points.trim();

          // Check if string contains newlines
          if (text.includes('\n')) {
            // Split by newlines and clean each point
            bulletPoints = text
              .split('\n')
              .map(point => point.trim().replace(/^[●•·\-*]\s*/, ''))
              .filter(point => point.length > 0);
          } else if (/[●•·]/.test(text)) {
            // No newlines but has bullet markers - split by bullet markers
            bulletPoints = text
              .split(/[●•·]/)
              .map(point => point.trim())
              .filter(point => point.length > 0);
          } else {
            // No newlines, no bullet markers - treat as single bullet point
            bulletPoints = [text];
          }
        } else if (Array.isArray(section.bullet_points)) {
          bulletPoints = section.bullet_points.map(point => {
            // Also clean array items if they have bullet markers
            return typeof point === 'string' ? point.trim().replace(/^[●•·\-*]\s*/, '') : point;
          });
        }
      }

      transformed[key] = {
        description: section.description || "",
        bullet_points: bulletPoints,
        footer: section.footer || "",
        is_number_list: section.is_number_list || 0
      };
    });
  }

  return transformed;
});

// Show job description dialog
const showJobDescription = () => {
  const container = document.createElement('div');

  const vueComponent = h(JobDescriptionContent, {
    parsedData: transformedParsedData.value,
    jobDetails: job.value
  });

  render(vueComponent, container);

  const dialog = new frappe.ui.Dialog({
    title: 'Job Description',
    size: 'extra-large',
    fields: [
      {
        fieldtype: 'HTML',
        fieldname: 'job_description_content'
      }
    ],
    primary_action_label: 'Close',
    primary_action: () => {
      dialog.hide();
    }
  });

  dialog.show();
  dialog.fields_dict.job_description_content.$wrapper.html(container);
};


const addCandidates = () => {
  frappe.set_route('job-applicant', 'new-job-applicant' , {
    designation : job.value.designation,
    job_opening: jobId.value
  });
};

// Move candidate to step
const moveCandidateToStep = () => {
  if (!activeCandidate.value) return;

  const dialog = new frappe.ui.Dialog({
    title: 'Move Candidate to Step',
    fields: [
      {
        fieldtype: 'Select',
        fieldname: 'target_step',
        label: 'Select Pipeline Step',
        options: stepOptions.value.map(step => step.label).join('\n'),
        reqd: 1
      },
      {
        fieldtype: 'Small Text',
        fieldname: 'comment',
        label: 'Comment (Optional)',
        description: 'Add a note about this move'
      }
    ],
    primary_action_label: 'Move',
    primary_action: async (values) => {
      const selectedStepLabel = values.target_step;
      const selectedStep = stepOptions.value.find(s => s.label === selectedStepLabel);

      if (!selectedStep) {
        frappe.msgprint('Please select a valid step');
        return;
      }

      // Check if already in this step
      if (selectedStep.value === activeStep.value) {
        frappe.msgprint({
          title: 'Info',
          message: 'Candidate is already in this step',
          indicator: 'orange'
        });
        dialog.hide();
        return;
      }

      try {
        await frm.call('move_applicant_to_another_step', {
          applicant_id: activeCandidate.value.job_applicant,
          new_step_code: selectedStep.value,
          comment: values.comment || ''
        });

        frappe.show_alert({
          message: `Candidate moved to ${selectedStepLabel}`,
          indicator: 'green'
        });
        dialog.hide();
        // Refresh job data
        getJobOpening();
      } catch (error) {
        frappe.msgprint({
          title: 'Error',
          message: 'Failed to move candidate',
          indicator: 'red'
        });
        console.error('Failed to move candidate:', error);
      }
    }
  });

  dialog.show();
};

// Bulk move candidates to step
const bulkMoveCandidates = () => {
  if (selectedCandidates.value.size === 0) {
    frappe.msgprint({
      title: 'No Selection',
      message: 'Please select at least one candidate to move',
      indicator: 'orange'
    });
    return;
  }

  const dialog = new frappe.ui.Dialog({
    title: `Move ${selectedCandidates.value.size} Candidate(s)`,
    fields: [
      {
        fieldtype: 'Select',
        fieldname: 'target_step',
        label: 'Select Pipeline Step',
        options: stepOptions.value.map(step => step.label).join('\n'),
        reqd: 1
      },
      {
        fieldtype: 'Small Text',
        fieldname: 'comment',
        label: 'Comment (Optional)',
        description: 'Add a note about this bulk move'
      }
    ],
    primary_action_label: 'Move All',
    primary_action: async (values) => {
      const selectedStepLabel = values.target_step;
      const selectedStep = stepOptions.value.find(s => s.label === selectedStepLabel);

      if (!selectedStep) {
        frappe.msgprint('Please select a valid step');
        return;
      }

      // Get applicant IDs from selected candidates
      const applicantIds = Array.from(selectedCandidates.value)
        .map(candidateId => {
          const candidate = filteredCandidates.value.find(c => c.name === candidateId);
          return candidate?.job_applicant;
        })
        .filter(Boolean);

      if (applicantIds.length === 0) {
        frappe.msgprint('No valid candidates to move');
        return;
      }

      try {
        await frm.call('move_applicants_to_another_step', {
          applicant_ids: applicantIds,
          new_step_code: selectedStep.value,
          comment: values.comment || ''
        });

        frappe.show_alert({
          message: `${applicantIds.length} candidate(s) moved to ${selectedStepLabel}`,
          indicator: 'green'
        });
        dialog.hide();
        // Clear selection and refresh
        selectedCandidates.value.clear();
        getJobOpening();
      } catch (error) {
        frappe.msgprint({
          title: 'Error',
          message: 'Failed to move candidates',
          indicator: 'red'
        });
        console.error('Failed to bulk move candidates:', error);
      }
    }
  });

  dialog.show();
};

// Assign Candidate Dialog
const assignCandidate = () => {
  if (!activeCandidate.value) return;

  const dialog = new frappe.ui.Dialog({
    title: `Assign ${activeCandidate.value.job_applicant}`,
    fields: [
      {
        fieldtype: 'MultiSelectPills',
        fieldname: 'assign_to',
        label: 'Assign To',
        reqd: 1,
        get_data: function(txt) {
          return frappe.db.get_link_options('User', txt, {
            user_type: 'System User',
            enabled: 1
          });
        }
      },
      {
        fieldtype: 'Date',
        fieldname: 'date',
        label: 'Complete By',
        default: frappe.datetime.add_days(frappe.datetime.get_today(), 7)
      },
      {
        fieldtype: 'Select',
        fieldname: 'priority',
        label: 'Priority',
        options: 'Low\nMedium\nHigh',
        default: 'Medium'
      },
      {
        fieldtype: 'Small Text',
        fieldname: 'description',
        label: 'Comment'
      }
    ],
    primary_action_label: 'Assign',
    primary_action: (values) => {
      if (!values.assign_to || values.assign_to.length === 0) {
        frappe.msgprint({
          title: 'Validation Error',
          message: 'Please select at least one user to assign',
          indicator: 'orange'
        });
        return;
      }

      // Prepare description (wrap in HTML if provided)
      let description = values.description || '';
      if (description) {
        description = `<div class="ql-editor read-mode"><p>${description}</p></div>`;
      }

      frappe.call({
        method: 'frappe.desk.form.assign_to.add',
        args: {
          doctype: 'Job Applicant',
          name: activeCandidate.value.job_applicant,
          assign_to: values.assign_to,
          date: values.date || null,
          priority: values.priority || 'Medium',
          description: description,
          assign_to_me: 0,
          bulk_assign: values.assign_to.length > 1 ? true : false
        },
        callback: function(res) {
          frappe.show_alert({
            message: `Assigned to ${values.assign_to.join(', ')}`,
            indicator: 'green'
          });
          dialog.hide();
        },
        error: function(err) {
          frappe.msgprint({
            title: 'Error',
            message: 'Failed to assign candidate',
            indicator: 'red'
          });
          console.error('Failed to assign candidate:', err);
        }
      });
    }
  });

  dialog.show();
};

// Share Candidate Dialog
const shareCandidate = () => {
  if (!activeCandidate.value) return;

  const dialog = new frappe.ui.Dialog({
    title: `Share ${activeCandidate.value.job_applicant}`,
    fields: [
      {
        fieldtype: 'Link',
        fieldname: 'user',
        label: 'User',
        options: 'User',
        reqd: 1,
        description: 'Select user to share with'
      },
      {
        fieldtype: 'Section Break',
        label: 'Permissions'
      },
      {
        fieldtype: 'Check',
        fieldname: 'read',
        label: 'Read',
        default: 1
      },
      {
        fieldtype: 'Column Break'
      },
      {
        fieldtype: 'Check',
        fieldname: 'write',
        label: 'Write',
        default: 0
      },
      {
        fieldtype: 'Column Break'
      },
      {
        fieldtype: 'Check',
        fieldname: 'submit',
        label: 'Submit',
        default: 0
      },
      {
        fieldtype: 'Column Break'
      },
      {
        fieldtype: 'Check',
        fieldname: 'share',
        label: 'Share',
        default: 0
      },
      {
        fieldtype: 'Section Break'
      },
      {
        fieldtype: 'Check',
        fieldname: 'notify',
        label: 'Notify user by email',
        default: 1
      }
    ],
    primary_action_label: 'Share',
    primary_action: (values) => {
      if (!values.user) {
        frappe.msgprint({
          title: 'Validation Error',
          message: 'Please select a user to share with',
          indicator: 'orange'
        });
        return;
      }

      frappe.call({
        method: 'frappe.share.add',
        args: {
          doctype: 'Job Applicant',
          name: activeCandidate.value.job_applicant,
          user: values.user,
          read: values.read ? 1 : 0,
          write: values.write ? 1 : 0,
          submit: values.submit ? 1 : 0,
          share: values.share ? 1 : 0,
          notify: values.notify ? 1 : 0
        },
        callback: function(res) {
          if (res.message) {
            frappe.show_alert({
              message: `Shared with ${values.user}`,
              indicator: 'green'
            });
            dialog.hide();
          }
        },
        error: function(err) {
          frappe.msgprint({
            title: 'Error',
            message: 'Failed to share candidate',
            indicator: 'red'
          });
          console.error('Failed to share candidate:', err);
        }
      });
    }
  });

  dialog.show();
};

// Transfer Candidate to Job (Copy or Move)
const transferCandidateToJob = (action = 'copy') => {
  if (!activeCandidate.value) return;

  const actionLabel = action === 'copy' ? 'Copy' : 'Move';
  const actionMethod = action === 'copy' ? 'copy_applicant_to_another_job' : 'move_applicant_to_another_job';

  const dialog = new frappe.ui.Dialog({
    title: `${actionLabel} ${activeCandidate.value.job_applicant} to Another Job`,
    fields: [
      {
        fieldtype: 'Link',
        fieldname: 'new_job_name',
        label: 'Destination Job',
        options: 'Job Opening',
        reqd: 1,
        description: `Select the job to ${action} this candidate to`,
        get_query: function() {
          return {
            filters: {
              name: ['!=', jobId.value],
              status: 'Open'
            }
          };
        },
        onchange: function() {
          const selectedJob = this.get_value();
          if (selectedJob) {
            // Fetch steps for selected job
            frappe.call({
              method: 'frappe.client.get',
              args: {
                doctype: 'Job Opening',
                name: selectedJob
              },
              callback: function(r) {
                if (r.message && r.message.custom_pipeline_steps) {
                  const steps = r.message.custom_pipeline_steps;
                  const stepOptions = steps.map(s => s.step_name).join('\n');
                  dialog.set_df_property('new_step', 'options', stepOptions);
                }
              }
            });
          }
        }
      },
      {
        fieldtype: 'Select',
        fieldname: 'new_step',
        label: 'Target Step',
        reqd: 1,
        description: 'Select which step to add the candidate to'
      },
      {
        fieldtype: 'Small Text',
        fieldname: 'comment',
        label: 'Comment (Optional)',
        description: `Add a note about this ${action} operation`
      }
    ],
    primary_action_label: `${actionLabel} Candidate`,
    primary_action: async (values) => {
      if (!values.new_job_name) {
        frappe.msgprint({
          title: 'Validation Error',
          message: 'Please select a destination job',
          indicator: 'orange'
        });
        return;
      }

      if (!values.new_step) {
        frappe.msgprint({
          title: 'Validation Error',
          message: 'Please select a target step',
          indicator: 'orange'
        });
        return;
      }

      // Get step_code from step_name
      frappe.call({
        method: 'frappe.client.get',
        args: {
          doctype: 'Job Opening',
          name: values.new_job_name
        },
        callback: function(r) {
          if (r.message && r.message.custom_pipeline_steps) {
            const steps = r.message.custom_pipeline_steps;
            const selectedStep = steps.find(s => s.step_name === values.new_step);

            if (selectedStep) {
              // Call the appropriate method based on action
              frm.call(actionMethod, {
                applicant_id: activeCandidate.value.job_applicant,
                new_job_name: values.new_job_name,
                new_step_code: selectedStep.step_code,
                comment: values.comment || ''
              }).then(() => {
                frappe.show_alert({
                  message: `Candidate ${action === 'copy' ? 'copied' : 'moved'} to ${values.new_job_name}`,
                  indicator: 'green'
                });
                dialog.hide();
                // Refresh job data if moved (to remove from current list)
                if (action === 'move') {
                  getJobOpening();
                }
              }).catch((error) => {
                frappe.msgprint({
                  title: 'Error',
                  message: `Failed to ${action} candidate to another job`,
                  indicator: 'red'
                });
                console.error(`Failed to ${action} candidate:`, error);
              });
            }
          }
        }
      });
    }
  });

  dialog.show();
};

// Copy to Job Dialog
const copyToJob = () => {
  transferCandidateToJob('copy');
};

// Move to Job Dialog
const moveToJob = () => {
  transferCandidateToJob('move');
};

// Assign Interview Dialog
const assignInterview = () => {
  if (!activeCandidate.value) return;

  // First, fetch interview rounds
  frappe.call({
    method: 'frappe.client.get_list',
    args: {
      doctype: 'Interview Round',
      fields: ['name', 'round_name'],
      order_by: 'idx asc'
    },
    callback: function(res) {
      const rounds = res.message || [];
      const roundOptions = rounds.length > 0
        ? rounds.map(r => r.round_name || r.name).join('\n')
        : 'HR Screening\nTechnical Interview\nFinal Interview';

      const dialog = new frappe.ui.Dialog({
        title: `Assign Interview to ${activeCandidate.value.job_applicant}`,
        fields: [
          {
            fieldtype: 'Select',
            fieldname: 'interview_round',
            label: 'Interview Round',
            options: roundOptions,
            reqd: 1
          },
          {
            fieldtype: 'Select',
            fieldname: 'status',
            label: 'Status',
            options: 'Pending\nUnder Review\nCleared\nRejected\nCancelled',
            default: 'Pending',
            reqd: 1
          },
          {
            fieldtype: 'Column Break'
          },
          {
            fieldtype: 'Date',
            fieldname: 'scheduled_on',
            label: 'Scheduled Date',
            reqd: 1
          },
          {
            fieldtype: 'Time',
            fieldname: 'from_time',
            label: 'From Time',
            reqd: 1
          },
          {
            fieldtype: 'Time',
            fieldname: 'to_time',
            label: 'To Time',
            reqd: 1
          },
          {
            fieldtype: 'Section Break'
          },
          {
            fieldtype: 'Float',
            fieldname: 'expected_average_rating',
            label: 'Expected Rating (0-5)',
            default: 0,
            description: 'Expected average rating from 0 to 5'
          },
          {
            fieldtype: 'Small Text',
            fieldname: 'interview_summary',
            label: 'Interview Summary',
            description: 'Optional notes or summary'
          }
        ],
        primary_action_label: 'Assign Interview',
        primary_action: (values) => {
          // Validation
          if (values.from_time >= values.to_time) {
            frappe.msgprint({
              title: 'Validation Error',
              message: 'End time must be after start time',
              indicator: 'orange'
            });
            return;
          }

          const payload = {
            job_applicant: activeCandidate.value.job_applicant,
            job_opening: jobId.value,
            designation: job.value.designation,
            interview_round: values.interview_round,
            status: values.status,
            scheduled_on: values.scheduled_on,
            from_time: values.from_time,
            to_time: values.to_time,
            expected_average_rating: values.expected_average_rating || 0,
            interview_summary: values.interview_summary || '',
            resume_link: activeCandidate.value.applicant_resume_link || '',
            reminded: 0
          };

          frappe.call({
            method: 'mawhub.interview_create_update',
            args: {payload},
            callback: function(res) {
              if (res.message) {
                frappe.show_alert({
                  message: `Interview assigned to ${activeCandidate.value.job_applicant} on ${values.scheduled_on}`,
                  indicator: 'green'
                });
                dialog.hide();
              }
            },
            error: function(err) {
              frappe.msgprint({
                title: 'Error',
                message: 'Failed to assign interview',
                indicator: 'red'
              });
              console.error('Failed to assign interview:', err);
            }
          });
        }
      });

      dialog.show();
    },
    error: function(err) {
      console.error('Failed to fetch interview rounds:', err);
      // Show dialog anyway with default options
      frappe.msgprint({
        title: 'Warning',
        message: 'Could not load interview rounds. Using defaults.',
        indicator: 'orange'
      });
    }
  });
};

// Action buttons configuration
const candidateActions = [
  {
    label: "Assign Interview",
    icon: "fa-calendar",
    action: assignInterview,
    variant: "default"
  },
  {
    label: "Share Candidate",
    icon: "fa-share",
    action: shareCandidate,
    variant: "default"
  },
  {
    label: "Send Email",
    icon: "fa-envelope",
    action: () => {
      frappe.msgprint("Send Email clicked");
    },
    variant: "default"
  },
  {
    label: "Assign",
    icon: "fa-user-plus",
    action: assignCandidate,
    variant: "default"
  },
  {
    label: "Copy To Job",
    icon: "fa-copy",
    action: copyToJob,
    variant: "default"
  },
  {
    label: "Move To Job",
    icon: "fa-edit",
    action: moveToJob,
    variant: "default"
  },
  {
    label: "Delete",
    icon: "fa-trash",
    action: () => {
      if (!activeCandidate.value) return;

      frappe.confirm(
        `Are you sure you want to remove ${activeCandidate.value.job_applicant} from this job?`,
        () => {
          frm.call('remove_applicant_from_step', {
            applicant_id: activeCandidate.value.job_applicant
          }).then(() => {
            frappe.show_alert({
              message: 'Candidate removed successfully',
              indicator: 'green'
            });
            // Refresh job data to update the list
            getJobOpening();
          }).catch((error) => {
            frappe.msgprint({
              title: 'Error',
              message: 'Failed to remove candidate',
              indicator: 'red'
            });
            console.error('Failed to remove candidate:', error);
          });
        }
      );
    },
    variant: "danger"
  }
];

onMounted(() => {
  jobId.value = frappe.get_route()[2];
  getJobOpening();
});
</script>

<template>
  <div class="jd-page">
    <!-- Loading state -->
    <div v-if="loading" class="jd-loading">
      <div style="text-align: center; padding: 50px; color: #888;">
        Loading job details...
      </div>
    </div>

    <!-- Main content -->
    <div v-else-if="job" class="jd-content">
      <!-- Header -->
      <div class="jd-header">
        <div>
          <div class="jd-title-row">
            <h2 class="jd-title">
              {{ job.designation || "Job Details" }}
            </h2>
            <div style="display: flex; gap: 8px;">
              <button class="btn btn-sm btn-default" @click="showJobDescription">
                <span class="fa fa-eye"></span> Show
              </button>
              <!-- <button class="btn btn-sm btn-default" @click="editJob">
                <span class="fa fa-edit"></span> Edit
              </button> -->
            </div>
          </div>
        </div>

        <div class="jd-header-actions">
          <!-- <button class="btn btn-default">
            <span class="fa fa-upload"></span> Upload Resume
          </button> -->
          <button @click="addCandidates" class="btn btn-default">
            <span class="fa fa-user-plus"></span> Add candidates
          </button>
        </div>
      </div>

      <!-- Pipeline tabs -->
      <div class="jd-pipeline-container">
        <div class="jd-pipeline">
          <div
            v-for="step in steps"
            :key="step.step_code"
            :class="['jd-step', { active: activeStep === step.step_code }]"
            @click="changeStep(step.step_code)"
          >
            {{ step.step_name }}
            <span class="count">{{ step.applicant_count || 0 }}</span>
          </div>
        </div>

      </div>

      <!-- Body -->
      <div class="jd-body">
        <!-- Left: Candidate list -->
        <div class="jd-left">
          <div class="jd-left-top">
            <input
              v-model="searchQuery"
              type="text"
              class="form-control input-sm"
              placeholder="Search by name, email..."
            />
            <div class="jd-bulk-toolbar ">
              <button class="btn btn-xs btn-default" @click="toggleSelectAll">
                <span :class="allSelected ? 'fa fa-check-square-o' : 'fa fa-square-o'"></span>
                {{ allSelected ? "Deselect All" : "Select All" }}
              </button>
              <div v-if="selectedCandidates.size > 0" class="jd-bulk-actions">
                <button class="btn btn-xs btn-default" @click="bulkMoveCandidates">
                  <span class="fa fa-arrow-right"></span> Bulk Move
                </button>
                <button class="btn btn-xs btn-default" @click="clearSelection">
                  <span class="fa fa-times"></span> Clear
                </button>
              </div>
            </div>
          </div>

          <div class="jd-candidate-list">
            <div
              v-for="candidate in filteredCandidates"
              :key="candidate.name"
              :class="['jd-item', { active: activeCandidateId === candidate.name }]"
              @click="selectCandidate(candidate.name)"
            >
              <input
                type="checkbox"
                class="jd-candidate-checkbox"
                :checked="selectedCandidates.has(candidate.name)"
                @click.stop="toggleCandidateSelection(candidate.name)"
              />
              <div class="jd-avatar">
                {{ candidate.job_applicant?.charAt(0).toUpperCase() }}
              </div>
              <div>
                <div class="jd-item-name">
                  {{ candidate.job_applicant }}
                </div>
                <div v-if="candidate.comment" class="jd-item-sub">
                   <p>{{ candidate.comment }}</p>
                </div>
              </div>
            </div>
            <div
              v-if="filteredCandidates.length === 0"
              class="text-muted"
              style="padding: 20px; text-align: center;"
            >
              No candidates found
            </div>
          </div>
        </div>

        <!-- Middle: Candidate details -->
        <div class="jd-middle">
          <div v-if="!activeCandidate" class="text-muted" style="padding: 40px; text-align: center;">
            Select a candidate from the list
          </div>
          <div v-else class="jd-middle-content">
            <div class="jd-detail-card">
              <div class="jd-detail-head">
                <div style="display: flex; align-items: center; gap: 12px;">
                  <div class="jd-avatar" style="width: 55px; height: 55px; font-size: 20px;">
                    {{ activeCandidate.job_applicant?.charAt(0).toUpperCase() }}
                  </div>
                  <div>
                    <h3 class="jd-detail-name">
                      {{ activeCandidate.job_applicant }}
                    </h3>
                    <div class="jd-detail-meta">
                      <a :href="`mailto:${activeCandidate.applicant_email}`">
                        {{ activeCandidate.job_applicant }}
                      </a>
                    </div>
                  </div>
                </div>
                <div style="display: flex; flex-direction: column; gap: 8px; min-width: 200px;">
                  <button
                    class="btn btn-sm btn-default"
                    @click="moveCandidateToStep"
                    style="display: flex; align-items: center; justify-content: center; gap: 6px;"
                  >
                    <span class="fa fa-arrow-right"></span>
                    <span>Move to Step</span>
                  </button>
                </div>
              </div>

              <!-- Tab Navigation -->
              <div class="jd-tabs-nav">
                <button
                  v-for="tab in tabs"
                  :key="tab.key"
                  :class="['jd-tab-button', { active: activeTab === tab.key }]"
                  @click="activeTab = tab.key"
                >
                  {{ tab.label }}
                </button>
              </div>

              <!-- Tab Content -->
              <div class="jd-tab-content">
                <component
                  :is="tabComponents[activeTab]"
                  :candidate="activeCandidate"
                  :job-id="jobId"
                />
              </div>
            </div>

            <!-- Actions at the bottom -->
            <div class="jd-actions-bottom">
              <div class="jd-actions-scroll">
                <button
                  v-for="action in candidateActions"
                  :key="action.label"
                  :class="['btn', 'btn-sm', action.variant === 'danger' ? 'btn-danger' : 'btn-default', 'jd-action-btn-horizontal']"
                  @click="action.action"
                >
                  <span :class="['fa', action.icon]"></span>
                  <span>{{ action.label }}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Error state -->
    <div v-else class="jd-error">
      <div style="text-align: center; padding: 50px; color: #d9534f;">
        No job data available. Please check the job ID.
      </div>
    </div>
  </div>
</template>
