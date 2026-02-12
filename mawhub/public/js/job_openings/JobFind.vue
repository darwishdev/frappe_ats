<script setup>
import { ref, computed, onMounted, getCurrentInstance, h, render } from "vue";
import JobDescriptionContent from "./components/JobDescriptionContent.vue";
import ApplicantProfile from "./components/ApplicantProfile.vue";
import ApplicantTimeline from "./components/ApplicantTimeline.vue";
import ApplicantCommunication from "./components/ApplicantCommunication.vue";
import ApplicantReview from "./components/ApplicantReview.vue";
import ApplicantComments from "./components/ApplicantComments.vue";

// Access frappe instance
const { proxy } = getCurrentInstance();
const frappe = proxy.$frappe;
const frm = proxy.$frm;

// State
const job = ref(null);
const steps = ref({});
const activeStep = ref("All");
const activeCandidateId = ref(null);
const selectedCandidates = ref(new Set());
const searchQuery = ref("");
const loading = ref(false);
const activeTab = ref("profile");

console.log("routesss")
// console.log(frappe.get_route())
const jobId = ref(frappe.get_route()[2]);

// Tab configuration
const tabs = [
  { key: "profile", label: "Profile" },
  { key: "timeline", label: "Timeline" },
  { key: "communication", label: "Communication" },
  { key: "review", label: "Review" },
  { key: "comments", label: "Comments" },
];

const tabComponents = {
  profile: ApplicantProfile,
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
    value: step.step_id,
  }));
});

const filteredCandidates = computed(() => {
  const currentStepData = steps.value[activeStep.value];
  if (!currentStepData?.candidates) return [];

  if (!searchQuery.value) {
    return currentStepData.candidates;
  }

  const query = searchQuery.value.toLowerCase();
  return currentStepData.candidates.filter((c) =>
    c.applicant_name?.toLowerCase().includes(query) ||
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

// Methods
// example to use frm.call
// const getJobOpening = async () => {
//   loading.value = true;
//
//   try {
//     const result = await frm.call("print_hello" ,
//     {
//       param1: "Ahmed",   // string argument
//       param2: 42         // integer argument
//     }); // matches Python method name
//     console.log("Server response:", result);      // should print "hello from server!"
//   } catch (error) {
//     console.error(error);
//   } finally {
//     loading.value = false;
//   }
// };
const getJobOpening = () => {
  loading.value = true;

  frappe.call({
    method: "mawhub.api.mawhub_job_opening_api.job_opening_find",
    args: {
      job: jobId.value,
    },
    callback: function(res) {
      loading.value = false;
      if (res.message) {
        job.value = res.message;
        // Build steps object
        setPipelineSteps(res.message.steps);
        frappe.show_alert({
          message: "Job details loaded successfully",
          indicator: "green"
        });
      }
    },
    error: function(r) {
      loading.value = false;
      frappe.msgprint({
        title: "Error", message: "Failed to load job details",
        indicator: "red"
      });
      console.error(r);
    }
  });
};

const setPipelineSteps = (stepsData) => {
  const stepsObj = {};
  stepsData.forEach((step) => {
    stepsObj[step.step_id] = step
  });
  steps.value = stepsObj;
  // Set first candidate as active if available
  if (steps.value[activeStep.value]?.candidates?.length > 0) {
    activeCandidateId.value = steps.value[activeStep.value].candidates[0].name;
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
      if (section.pullet_points) {
        try {
          bulletPoints =
            typeof section.pullet_points === "string"
              ? JSON.parse(section.pullet_points)
              : section.pullet_points;
        } catch (e) {
          console.error("Failed to parse bullet points:", e);
          bulletPoints = [];
        }
      }

      transformed[key] = {
        description: section.description || "",
        bullet_points: Array.isArray(bulletPoints) ? bulletPoints : [],
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


const editJob = () => {
  frappe.set_route('job-opening', jobId.value);
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
      }
    ],
    primary_action_label: 'Move',
    primary_action: (values) => {
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

      // TODO: Implement actual API call to move candidate
      const formData = new FormData();
      formData.append('names', JSON.stringify([activeCandidate.value.name]));
      formData.append('pipeline_step', selectedStep.value);

      frappe.call({
        method: "mawhub.api.mawhub_job_applicant_api.job_applicant_bulk_update",
        args: {
          payload: formData
        },
        callback: function(r) {
          if (r.message) {
            frappe.show_alert({
              message: `Candidate moved to ${selectedStepLabel}`,
              indicator: 'green'
            });
            dialog.hide();
            // Refresh job data
            getJobOpening();
          }
        },
        error: function(r) {
          frappe.msgprint({
            title: 'Error',
            message: 'Failed to move candidate',
            indicator: 'red'
          });
        }
      });
    }
  });

  dialog.show();
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
            method: 'mawhub.api.mawhub_interview_api.interview_create_update',
            args: payload,
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
    action: () => {
      frappe.msgprint("Share Candidate clicked");
    },
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
    label: "Print",
    icon: "fa-print",
    action: () => {
      frappe.msgprint("Send Email clicked");
    },
    variant: "default"
  },
  {
    label: "Copy To Job",
    icon: "fa-copy",
    action: () => {
      frappe.msgprint("Copy To Job clicked");
    },
    variant: "default"
  },
  {
    label: "Move To Job",
    icon: "fa-edit",
    action: () => {
      frappe.msgprint("Move To Job clicked");
    },
    variant: "default"
  },
  {
    label: "Delete",
    icon: "fa-trash",
    action: () => {
      frappe.confirm(
        "Are you sure you want to delete this candidate?",
        () => {
          frappe.msgprint("Candidate deleted");
        }
      );
    },
    variant: "danger"
  }
];

onMounted(() => {
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
              <button class="btn btn-sm btn-default" @click="editJob">
                <span class="fa fa-edit"></span> Edit
              </button>
            </div>
          </div>
        </div>

        <div class="jd-header-actions">
          <button class="btn btn-default">
            <span class="fa fa-upload"></span> Upload Resume
          </button>
          <button @click="addCandidates" class="btn btn-default">
            <span class="fa fa-user-plus"></span> Add candidates
          </button>
        </div>
      </div>

      <!-- Pipeline tabs -->
      <div class="jd-pipeline-container">
        <div class="jd-pipeline">
          <div
            v-for="step in Object.values(steps)"
            :key="step.step_id"
            :class="['jd-step', { active: activeStep === step.step_id }]"
            @click="changeStep(step.step_id)"
          >
            {{ step.step_name }}
            <span class="count">{{ step.candidate_count || 0 }}</span>
          </div>
        </div>
        <button class="btn btn-sm btn-default">
          <span class="fa fa-cog"></span> Edit Pipeline
        </button>
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
                <button class="btn btn-xs btn-default">
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
          <div class="jd-detail-card">
            <div v-if="!activeCandidate" class="text-muted" style="padding: 40px; text-align: center;">
              Select a candidate from the list
            </div>
            <div v-else>
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
          </div>
        </div>

        <!-- Right: Actions panel -->
        <div class="jd-actions-panel">
          <div v-if="!activeCandidate" class="text-muted" style="padding: 20px; text-align: center;">
            Select a candidate
          </div>
          <div v-else class="jd-actions-content">
            <h4 class="jd-actions-title">Actions</h4>
            <div class="jd-actions-buttons">
              <button
                v-for="action in candidateActions"
                :key="action.label"
                :class="['btn', 'btn-sm', action.variant === 'danger' ? 'btn-danger' : 'btn-default', 'action-btn', 'flex', 'flex-column', 'items-center', 'p-3']"
                @click="action.action"
              >
                <span :class="['pb-1', 'fa', action.icon]"></span>
                <span>{{ action.label }}</span>
              </button>
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
