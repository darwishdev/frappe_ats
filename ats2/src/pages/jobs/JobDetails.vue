<template>
    <div class="jd-page">
        <!-- Loading state -->
        <div v-if="jobDetailsResource.loading" class="jd-loading">
            <div class="text-center py-8 text-gray-500">Loading job details...</div>
        </div>

        <!-- Error state -->
        <div v-else-if="jobDetailsResource.error" class="jd-error">
            <div class="text-center py-8 text-red-500">
                Error loading job details: {{ jobDetailsResource.error }}
            </div>
        </div>

        <!-- Header -->
        <div v-else class="jd-content">
            <div class="jd-header">
                <div>
                    <div class="jd-title-row">
                        <h2 class="jd-title">{{ job?.title || "Job Details" }}</h2>
                        <Button size="sm" @click="editJob">Edit</Button>
                    </div>
                    <div class="jd-subtitle">
                        {{ job?.department }} · {{ job?.work_mode }} · {{ job?.location }}
                    </div>
                </div>

                <div class="jd-header-actions">
                    <input
                        ref="resumeFileInput"
                        type="file"
                        accept=".pdf,.doc,.docx"
                        style="display: none"
                        @change="handleResumeUpload"
                    />
                    <Button
                        theme="gray"
                        :variant="'solid'"
                        class="w-40"
                        :loading="isUploading"
                        @click="triggerResumeUpload"
                    >
                        {{ isUploading ? `Uploading... ${uploadProgress}%` : 'Upload Resume' }}
                    </Button>
                    <Button
                        theme="gray"
                        :variant="'solid'"
                        class="w-40"
                        @click="redirectToAddCandidates"
                        >Add candidates</Button
                    >
                </div>
            </div>

            <!-- Pipeline tabs -->
            <div class="jd-pipeline">
                <div
                    v-for="step in job?.pipeline_steps"
                    :key="step.key"
                    :class="['jd-step', { active: activeStep === step.key }]"
                    @click="changeStep(step.key)"
                >
                    {{ step.label }} <span class="count">{{ getStepCount(step.key) }}</span>
                </div>
            </div>

            <!-- Body -->
            <div class="jd-body">
                <!-- Left: list -->
                <div class="jd-left">
                    <div class="jd-left-top">
                        <TextInput
                            v-model="searchQuery"
                            type="text"
                            size="sm"
                            variant="subtle"
                            placeholder="Search by name, skills, tags..."
                        />
                        <div class="jd-bulk-toolbar">
                            <Button size="sm" @click="toggleSelectAll">
                                {{ allSelected ? "Deselect All" : "Select All" }}
                            </Button>
                            <div v-if="selectedCandidates.size > 0" class="jd-bulk-actions">
                                <Button
                                    size="sm"
                                    theme="gray"
                                    :variant="'solid'"
                                    @click="showBulkMoveDialog = true"
                                >
                                    Bulk Move
                                </Button>
                                <Button size="sm" @click="clearSelection">Clear</Button>
                            </div>
                        </div>
                    </div>
                    <div class="jd-candidate-list">
                        <div
                            v-for="candidate in filteredCandidates"
                            :key="candidate.id"
                            :class="['jd-item', { active: activeCandidateId === candidate.id }]"
                            @click="selectCandidate(candidate.id)"
                        >
                            <input
                                type="checkbox"
                                class="jd-candidate-checkbox"
                                :checked="selectedCandidates.has(candidate.id)"
                                @click.stop="toggleCandidateSelection(candidate.id)"
                            />
                            <div class="jd-avatar">
                                {{ candidate.name?.charAt(0).toUpperCase() }}
                            </div>
                            <div>
                                <div class="jd-item-name">{{ candidate.name }}</div>
                                <div class="jd-item-sub">
                                    via <b>{{ candidate.source }}</b> ·
                                    {{ formatDate(candidate.created_at) }}
                                </div>
                            </div>
                        </div>
                        <div
                            v-if="filteredCandidates.length === 0"
                            class="text-muted"
                            style="padding: 10px"
                        >
                            No candidates
                        </div>
                    </div>
                </div>

      <!-- Middle: details -->
      <div class="jd-middle">
        <div class="jd-detail-card">
          <div v-if="!activeCandidate" class="text-muted">
            Select a candidate from the list.
          </div>
          <div v-else>
            <div class="jd-detail-head">
              <div style="display: flex; align-items: center; gap: 12px">
                <div class="jd-avatar" style="width: 48px; height: 48px; font-size: 20px">
                  {{ activeCandidate.name?.charAt(0).toUpperCase() }}
                </div>
                <div>
                  <h3 class="jd-detail-name">{{ activeCandidate.name }}</h3>
                  <div class="jd-detail-meta">
                    {{ activeCandidate.designation || activeCandidate.email }}
                  </div>
                </div>
              </div>
                <div
                    style="
                        display: flex;
                        flex-direction: column;
                        gap: 8px;
                        min-width: 200px;
                    "
                >
                    <Select
                        v-model="targetStep"
                        :options="stepOptions"
                        placeholder="Select step"
                    />
                    <Button
                        size="sm"
                        theme="gray"
                        :variant="'solid'"
                        @click="moveCandidateToStep"
                    >
                        Move to selected step
                    </Button>
                </div>
            </div>

            <div>
              <div class="jd-badges">
                <span class="jd-badge">📧 {{ activeCandidate.email }}</span>
                <span class="jd-badge">☎ {{ activeCandidate.phone }}</span>
                <span class="jd-badge">🌍 {{ activeCandidate.country }}</span>
              </div>
              <div class="jd-badges" style="margin-top: 8px">
                <span class="jd-badge">Status: {{ activeCandidate.status }}</span>
                <span class="jd-badge">Source: {{ activeCandidate.source }}</span>
                <span class="jd-badge">Rating: {{ getRatingStars(activeCandidate.rating) }}</span>
              </div>
              <div class="jd-badges" style="margin-top: 8px">
                <span class="jd-badge">Current Stage: {{ activeCandidate.stage_name }}</span>
                <span class="jd-badge">Applied: {{ formatDate(activeCandidate.created_at) }}</span>
              </div>
              <div
                v-if="activeCandidate.cover_letter"
                style="
                  margin-top: 12px;
                  padding: 10px;
                  background: #f9fafb;
                  border-radius: 6px;
                "
              >
                <strong>Cover Letter:</strong>
                <p style="margin: 4px 0 0 0; color: #6b7280">
                  {{ activeCandidate.cover_letter }}
                </p>
              </div>
              <div v-if="activeCandidate.resume_link" style="margin-top: 8px">
                <Button
                  size="sm"
                  @click="window.open(activeCandidate.resume_link, '_blank')"
                >
                  📄 View Resume
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: action panel -->
      <div class="jd-actions-panel !w-[12rem]">
        <div v-if="!activeCandidate" class="text-muted">
          Select a candidate
        </div>
        <div v-else class="jd-actions-content">
          <!-- <h4 class="jd-actions-title">Actions</h4> -->
          <div class="jd-actions-buttons !w-[10rem]">
            <Button
              size="md"
              theme="gray"
              :variant="'solid'"
              class="jd-action-btn !w-[10rem]"
              @click="viewApplicantProfile"
            >
              <!-- <span class="jd-action-icon">👤</span> -->
              <span>View Profile</span>
            </Button>
            <Button
              size="md"
              theme="gray"
              :variant="'solid'"
              class="jd-action-btn !w-[10rem]"
              @click="showAssignInterviewDialog = true"
            >
              <!-- <span class="jd-action-icon">📅</span> -->
              <span>Assign Interview</span>
            </Button>
            <Button
              size="md"
              theme="gray"
              :variant="'solid'"
              class="jd-action-btn !w-[10rem]"
              @click="sendEmail"
            >
              <!-- <span class="jd-action-icon">✉️</span> -->
              <span>Send Email</span>
            </Button>
          </div>
        </div>
      </div>
    </div>

            <!-- Dialog Components -->
            <AddCandidateDialog
                v-model="showAddCandidateDialog"
                :on-submit="handleAddCandidate"
            />

            <AssignInterviewDialog
                v-model="showAssignInterviewDialog"
                :candidate-id="activeCandidate?.id"
                :candidate-name="activeCandidate?.name"
                :on-submit="handleAssignInterview"
            />

            <BulkMoveDialog
                v-model="showBulkMoveDialog"
                :step-options="stepOptions"
                :candidate-count="selectedCandidates.size"
                :on-submit="handleBulkMove"
            />

            <ApplicantProfileDialog
                v-model="showProfileDialog"
                :applicant-id="activeCandidate?.id"
                :candidate-name="activeCandidate?.name"
                :on-fetch-profile="fetchApplicantProfile"
            />

            <SendEmailDialog
                v-model="showSendEmailDialog"
                :candidate-email="activeCandidate?.email"
                :candidate-name="activeCandidate?.name"
                :job-title="job?.title"
                :on-submit="handleSendEmail"
            />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { TextInput, Select, Button, createResource } from "frappe-ui";
import { useToast } from "vue-toastification";
import { JobDetailsAPI } from "../../api/apiClient.js";
import AddCandidateDialog from "../../components/jobs/AddCandidateDialog.vue";
import AssignInterviewDialog from "../../components/jobs/AssignInterviewDialog.vue";
import BulkMoveDialog from "../../components/jobs/BulkMoveDialog.vue";
import ApplicantProfileDialog from "../../components/jobs/ApplicantProfileDialog.vue";
import SendEmailDialog from "../../components/jobs/SendEmailDialog.vue";

const toast = useToast();

const route = useRoute();
const router = useRouter();

JobDetailsAPI.init(createResource);
// Get job ID from route
const jobId = computed(() => route.params.jobId || route.query.job || "HR-OPN-2026-0002");

// Create resource for fetching job details
const jobDetailsResource = createResource({
    url: "mawhub.job_opening_find",
    params: {
        job: jobId.value,
    },
    auto: true,
    onSuccess(data) {
        if (data) {
            const transformedData = transformJobData(data);
            job.value = transformedData;
            candidates.value = transformedData.candidates;
            activeStep.value = "all";
            activeCandidateId.value = candidates.value[0]?.id || null;

            if (activeCandidate.value) {
                targetStep.value = activeCandidate.value.stage;
            }
        }
    },
    onError(error) {
        console.error("Error loading job details:", error);
        toast.error(`Error loading job details: ${error.message || "Unknown error"}`);
    },
});

// State
const job = ref(null);
const candidates = ref([]);
const activeStep = ref("all");
const activeCandidateId = ref(null);
const selectedCandidates = ref(new Set());
const searchQuery = ref("");
const targetStep = ref("");

// Dialog states
const showAddCandidateDialog = ref(false);
const showAssignInterviewDialog = ref(false);
const showBulkMoveDialog = ref(false);
const showProfileDialog = ref(false);
const showSendEmailDialog = ref(false);

// Resume upload state
const resumeFileInput = ref(null);
const isUploading = ref(false);
const uploadProgress = ref(0);

// Computed properties
const stepOptions = computed(() => {
    if (!job.value?.steps) return [];
    return job.value.steps.map((step) => ({
        label: step.label,
        value: step.key,
    }));
});

const filteredCandidates = computed(() => {
    let list = candidates.value;

    // Filter by active step
    if (activeStep.value !== "all") {
        list = list.filter((c) => c.stage === activeStep.value);
    }

    // Filter by search query
    const q = searchQuery.value.toLowerCase().trim();
    if (q) {
        list = list.filter((c) => {
            const searchText =
                `${c.name} ${c.email} ${c.country} ${c.designation} ${c.source}`.toLowerCase();
            return searchText.includes(q);
        });
    }

    return list;
});

const activeCandidate = computed(() => {
    return candidates.value.find((c) => c.id === activeCandidateId.value) || null;
});

const allSelected = computed(() => {
    return (
        filteredCandidates.value.length > 0 &&
        selectedCandidates.value.size === filteredCandidates.value.length
    );
});

// Methods
function transformJobData(rawJob) {
    const stepsMap = new Map();
    const allCandidates = [];

    if (rawJob.steps && Array.isArray(rawJob.steps)) {
        rawJob.steps.forEach((step) => {
            const stepKey = `${step.step_id}`;
            if (!stepsMap.has(stepKey)) {
                stepsMap.set(stepKey, {
                    key: stepKey,
                    label: step.step_name,
                    id: step.step_id,
                    idx: step.step_idx,
                    type: step.step_type,
                });
            }

            if (step.candidates && Array.isArray(step.candidates)) {
                step.candidates.forEach((candidate) => {
                    // Skip candidates without valid ID or email
                    if (!candidate["applicant_id,"] && !candidate["applicant_email,"]) {
                        return;
                    }

                    const candidateId =
                        candidate["applicant_id,"] || candidate["applicant_email,"];
                    const existingIdx = allCandidates.findIndex((c) => c.id === candidateId);
                    if (existingIdx === -1) {
                        allCandidates.push({
                            id: candidateId,
                            name: candidate["applicant_name,"],
                            email: candidate["applicant_email,"],
                            phone: candidate["applicant_phone,"] || "N/A",
                            country: candidate["applicant_country,"] || "N/A",
                            designation: candidate["applicant_designation,"],
                            status: candidate["applicant_status,"],
                            source: candidate["applicant_source,"] || "Unknown",
                            rating: candidate["applicant_rating,"] || 0,
                            resume_link: candidate["applicant_resume_link,"] || null,
                            cover_letter: candidate["applicant_cover_letter,"] || null,
                            stage: stepKey,
                            stage_name: step.step_name,
                            created_at: candidate["applicant_created_at,"],
                        });
                    }
                });
            }
        });
    }

    const steps = Array.from(stepsMap.values()).sort((a, b) => a.idx - b.idx);

    const pipeline_steps = [{ key: "all", label: "All" }, ...steps];

    return {
        name: rawJob.name,
        title: rawJob.designation || "Untitled Position",
        department: rawJob.department || "Not Specified",
        location: rawJob.location || "Not Specified",
        work_mode: rawJob.employment_type || "Full-time",
        pipeline_steps: pipeline_steps,
        steps: steps,
        candidates: allCandidates,
    };
}

function getStepCount(stepKey) {
    if (stepKey === "all") return candidates.value.length;
    return candidates.value.filter((c) => c.stage === stepKey).length;
}

function changeStep(stepKey) {
    activeStep.value = stepKey;
    selectedCandidates.value.clear();

    // Reset active candidate if not in filtered list
    if (!filteredCandidates.value.some((c) => c.id === activeCandidateId.value)) {
        activeCandidateId.value = filteredCandidates.value[0]?.id || null;
    }
}

function selectCandidate(candidateId) {
    activeCandidateId.value = candidateId;
    if (activeCandidate.value) {
        targetStep.value = activeCandidate.value.stage;
    }
}

function toggleCandidateSelection(candidateId) {
    if (selectedCandidates.value.has(candidateId)) {
        selectedCandidates.value.delete(candidateId);
    } else {
        selectedCandidates.value.add(candidateId);
    }
    // Force reactivity
    selectedCandidates.value = new Set(selectedCandidates.value);
}

function toggleSelectAll() {
    if (allSelected.value) {
        selectedCandidates.value.clear();
    } else {
        filteredCandidates.value.forEach((c) => selectedCandidates.value.add(c.id));
    }
    selectedCandidates.value = new Set(selectedCandidates.value);
}

function clearSelection() {
    selectedCandidates.value.clear();
    selectedCandidates.value = new Set();
}

function getRatingStars(rating) {
    const stars = Math.max(0, Math.min(5, Math.floor(rating)));
    return stars > 0 ? "⭐".repeat(stars) : "Not rated";
}

function formatDate(dateStr) {
    if (!dateStr) return "Recently";
    try {
        const date = new Date(dateStr);
        const now = new Date();
        const diff = now - date;
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));

        if (days === 0) return "Today";
        if (days === 1) return "Yesterday";
        if (days < 7) return `${days} days ago`;
        if (days < 30) return `${Math.floor(days / 7)} weeks ago`;
        return date.toLocaleDateString();
    } catch {
        return "Recently";
    }
}

function editJob() {
    window.open(`http://localhost:8001/desk/job-opening/${job.value?.name}`, "_blank");
}

// Handler functions for dialog components
async function handleAddCandidate(formData) {
    if (!formData.name || !formData.email) {
        toast.warning("Please fill in required fields");
        throw new Error("Required fields missing");
    }

    try {
        await JobDetailsAPI.addCandidate(job.value.name, {
            candidate_name: formData.name,
            candidate_email: formData.email,
            phone: formData.phone,
            country: formData.country,
            source: formData.source,
        });

        toast.success("Candidate added successfully");
        reloadJobDetails();
    } catch (error) {
        toast.error(error.message || "Failed to add candidate");
        throw error;
    }
}

const redirectToAddCandidates = () => {
    window.open(`http://localhost:8001/desk/job-applicant/new-job-applicant`, "_blank");
};

// Resume upload functions
function triggerResumeUpload() {
    if (resumeFileInput.value) {
        resumeFileInput.value.click();
    }
}

async function handleResumeUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file type
    const validTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    if (!validTypes.includes(file.type)) {
        toast.error('Please upload a PDF or Word document');
        return;
    }

    // Validate file size (max 10MB)
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
        toast.error('File size must be less than 10MB');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('is_private', 1);
   // formData.append('folder', 'Home/Resumes');

    try {
        isUploading.value = true;
        uploadProgress.value = 0;

        const response = await fetch('/api/method/upload_file', {
            method: 'POST',
            headers: {
                'X-Frappe-CSRF-Token': window.frappe?.csrf_token || '',
            },
            body: formData
        });

        if (!response.ok) {
            throw new Error('Upload failed');
        }

        const result = await response.json();
        
        if (result.message && result.message.file_url) {
            uploadProgress.value = 100;
            toast.success('Resume uploaded successfully');
            console.log('File Uploaded:', result.message.file_url);
            
            // Parse the resume
            await parseResume(result.message.file_url, result.message.name);
        } else {
            throw new Error('Invalid response from server');
        }
    } catch (error) {
        console.error('Upload failed:', error);
        toast.error(`Upload failed: ${error.message || 'Unknown error'}`);
    } finally {
        isUploading.value = false;
        uploadProgress.value = 0;
        // Reset file input
        if (resumeFileInput.value) {
            resumeFileInput.value.value = '';
        }
    }
}

async function parseResume(fileUrl, fileName) {
    try {
        toast.info('Parsing resume...');
        
        // Call the resume parsing API with progress callback
        const response = await JobDetailsAPI.parseResume(
            {
                path: fileUrl,
                file_name: fileName,
                job_opening: job.value.name,
                activeStep : activeStep.value
            },
            (progressData) => {
                // Handle progress updates from the EventStream
                console.log('Resume parsing step:', progressData);
                
                // You can show progress toasts or update UI here
                if (progressData.status) {
                    toast.info(progressData.status);
                } else if (progressData.step) {
                    toast.info(`Parsing ${progressData.step}...`);
                }
            }
        );
        
        if (response) {
            toast.success('Resume parsed successfully! Candidate added.');
            // Reload job details to show the new candidate
            reloadJobDetails();
        }
    } catch (error) {
        console.error('Resume parsing failed:', error);
        toast.error(`Resume parsing failed: ${error.message || 'Unknown error'}`);
    }
}

async function moveCandidateToStep() {
    if (!activeCandidate.value || !targetStep.value) return;

    if (targetStep.value === activeCandidate.value.stage) {
        toast.warning("Candidate is already in this stage");
        return;
    }

    const targetStepName =
        job.value.steps.find((s) => s.key === targetStep.value)?.label || targetStep.value;

    const payload = {
        names: [activeCandidate.value.id],
        pipeline_step: targetStep.value,
        status: activeCandidate.value.status,
    };

    try {
        const response = await JobDetailsAPI.bulkUpdateApplicants(payload);
        toast.success(`${activeCandidate.value.name} moved to "${targetStepName}"`);
        
        // Update local state
        const candidate = candidates.value.find((c) => c.id === activeCandidate.value.id);
        if (candidate) {
            candidate.stage = targetStep.value;
            candidate.stage_name = targetStepName;
        }
        changeStep(targetStep.value)
    } catch (error) {
        console.log(error);

        toast.error(error.message || "Failed to move candidate");
    }
}

async function handleAssignInterview(formData) {
    if (
        !formData.interview_round ||
        !formData.status ||
        !formData.scheduled_on ||
        !formData.from_time ||
        !formData.to_time
    ) {
        toast.warning("Please fill in all required fields");
        throw new Error("Required fields missing");
    }

    if (formData.from_time >= formData.to_time) {
        toast.warning("End time must be after start time");
        throw new Error("Invalid time range");
    }

  const payload = {
    job_applicant: activeCandidate.value.id,
    interview_round: formData.interview_round,
    status: formData.status,
    scheduled_on: formData.scheduled_on,
    from_time: formData.from_time,
    to_time: formData.to_time,
    expected_average_rating: formData.expected_average_rating || 0,
    interview_summary: formData.interview_summary || "",
  };

  try {
    await JobDetailsAPI.createOrUpdateInterview(payload);
    toast.success(`Interview assigned to ${activeCandidate.value?.name} on ${formData.scheduled_on}`);
  } catch (error) {
    toast.error(error.message || "Failed to assign interview");
    throw error;
  }
}

async function handleBulkMove(formData) {
    if (!formData.target_step) {
        toast.warning("Please select a target step");
        throw new Error("Target step required");
    }

    const targetStepLabel =
        job.value.steps.find((s) => s.key === formData.target_step)?.label || "";

    const payload = {
        names: Array.from(selectedCandidates.value),
        pipeline_step: formData.target_step,
    };

    if (formData.status) {
        payload.status = formData.status;
    }

    try {
        const response = await JobDetailsAPI.bulkUpdateApplicants(payload);

        toast.success(
            `${selectedCandidates.value.size} candidate(s) moved to "${targetStepLabel}"`,
        );

        // Update local state
        selectedCandidates.value.forEach((candidateId) => {
            const candidate = candidates.value.find((c) => c.id === candidateId);
            if (candidate) {
                candidate.stage = formData.target_step;
                candidate.stage_name = targetStepLabel;
                if (formData.status) {
                    candidate.status = formData.status;
                }
            }
        });
        changeStep(formData.target_step)
        clearSelection();
    } catch (error) {
        toast.error(error.message || "Failed to move candidates");
        console.log(error);
        
        throw error;
    }
}

// Reload job details
function reloadJobDetails() {
    jobDetailsResource.fetch();
}

// Action panel methods
function viewApplicantProfile() {
  if (!activeCandidate.value) return;
  showProfileDialog.value = true;
}

async function fetchApplicantProfile(applicantId) {
  try {
    const profile = await JobDetailsAPI.jobApplicantFind(applicantId);
    return profile;
  } catch (error) {
    toast.error('Failed to load profile');
    console.error(error);
    throw error;
  }
}

function sendEmail() {
  if (!activeCandidate.value) return;
  showSendEmailDialog.value = true;
}

async function handleSendEmail(formData) {
  if (!formData.to || !formData.subject || !formData.message) {
    toast.warning('Please fill in all required fields');
    throw new Error('Required fields missing');
  }

  try {
    // Call the email API
    await JobDetailsAPI.sendEmail({
      recipient: formData.to,
      subject: formData.subject,
      message: formData.message,
      cc: formData.cc,
      bcc: formData.bcc,
      send_me_a_copy: formData.send_me_a_copy,
      job_applicant: activeCandidate.value.id,
      job_opening: job.value.name,
    });

    toast.success(`Email sent successfully to ${formData.to}`);
  } catch (error) {
    toast.error(error.message || 'Failed to send email');
    throw error;
  }
}

// Watch for search query changes
watch(searchQuery, () => {
    if (!filteredCandidates.value.some((c) => c.id === activeCandidateId.value)) {
        activeCandidateId.value = filteredCandidates.value[0]?.id || null;
    }
});

// Watch for route changes
watch(
    () => route.params.jobId,
    (newJobId) => {
        if (newJobId) {
            jobDetailsResource.update({
                params: { job: newJobId },
            });
            jobDetailsResource.fetch();
        }
    },
);
</script>

<style scoped>
.jd-page {
    padding: 2rem;
}

.jd-header {
    display: flex;
    justify-content: space-between;
    gap: 16px;
    align-items: flex-start;
    margin-bottom: 12px;
}

.jd-header-actions {
    display: flex;
    gap: 12px;
    align-items: center;
}

.jd-title-row {
    display: flex;
    gap: 10px;
    align-items: center;
}

.jd-title {
    margin: 0;
    font-size: 28px;
    font-weight: 800;
}

.jd-subtitle {
    color: #6b7280;
    margin-top: 6px;
}

.jd-pipeline {
    display: flex;
    gap: 10px;
    align-items: center;
    overflow: auto;
    padding: 10px 0;
    border-bottom: 1px solid var(--border-color, #eee);
    margin-bottom: 12px;
}

.jd-step {
    white-space: nowrap;
    padding: 8px 10px;
    border-radius: 8px;
    border: 1px solid var(--border-color, #e6e6e6);
    cursor: pointer;
    background: #fff;
    color: #111827;
    font-weight: 600;
    font-size: 13px;
}

.jd-step.active {
    background: #111827;
    color: #fff;
    border-color: #111827;
}

.jd-step .count {
    opacity: 0.9;
    margin-left: 6px;
    font-weight: 800;
}

.jd-body {
  display: grid;
  grid-template-columns: 350px 1fr 190px;
  gap: 14px;
  min-height: 520px;
}

.jd-left,
.jd-middle,
.jd-actions-panel {
  background: #ffffff66;
  border: 1px solid var(--border-color, #e6e6e6);
  border-radius: 10px;
}

.jd-actions-panel {
  display: flex;
  flex-direction: column;
}

.jd-actions-content {
  padding: 14px;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.jd-actions-title {
  font-size: 16px;
  font-weight: 700;
  color: #111827;
  margin: 0 0 16px 0;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-color, #e6e6e6);
}

.jd-actions-buttons {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.jd-action-icon {
  font-size: 18px;
  line-height: 1;
}

.jd-left-top {
    padding: 12px;
    border-bottom: 1px solid var(--border-color, #eee);
}

.jd-bulk-toolbar {
    display: flex;
    gap: 8px;
    align-items: center;
    margin-top: 10px;
    justify-content: space-between;
}

.jd-bulk-actions {
    display: flex;
    gap: 8px;
    align-items: center;
}

.jd-candidate-list {
    padding: 6px;
    max-height: 680px;
    overflow: auto;
}

.jd-item {
    display: flex;
    gap: 10px;
    align-items: center;
    padding: 10px;
    border-radius: 8px;
    cursor: pointer;
    margin: 7px 0;
}

.jd-item:hover {
    background: #f7f7f7;
}

.jd-item.active {
    background: #e5e5e59e;
}

.jd-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: #e5e7eb;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    color: #374151;
}

.jd-item-name {
    font-weight: 800;
    color: black;
}

.jd-item-sub {
    color: #6b7280;
    font-size: 12px;
    margin-top: 2px;
}

.jd-detail-card {
    padding: 14px;
}

.jd-detail-head {
    display: flex;
    justify-content: space-between;
    gap: 14px;
    align-items: flex-start;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--border-color, #e6e6e6);
    margin-bottom: 16px;
}

.jd-detail-name {
    font-size: 22px;
    font-weight: 900;
    margin: 0;
    color: #111827;
}

.jd-badges {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-top: 8px;
}

.jd-badge {
    font-size: 12px;
    background: #f3f4f6;
    border: 1px solid #e5e7eb;
    border-radius: 999px;
    padding: 4px 8px;
    color: #111827;
}

.jd-detail-meta {
    color: #6b7280;
    margin-top: 2px;
    font-size: 14px;
}

.jd-candidate-checkbox {
    cursor: pointer;
    width: 16px;
    height: 16px;
}

.text-muted {
    color: #6b7280;
    text-align: center;
}

.space-y-4 > * + * {
    margin-top: 1rem;
}

.grid {
    display: grid;
}

.grid-cols-2 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
}

.grid-cols-3 {
    grid-template-columns: repeat(3, minmax(0, 1fr));
}

.gap-4 {
    gap: 1rem;
}

.form-control {
    width: 100%;
    padding: 8px 12px;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    font-size: 14px;
    outline: none;
    transition: border-color 0.2s;
}

.form-control:focus {
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

label {
    font-size: 14px;
    color: #374151;
}

.block {
    display: block;
}

.text-sm {
    font-size: 0.875rem;
}

.font-medium {
    font-weight: 500;
}

.mb-1 {
    margin-bottom: 0.25rem;
}
</style>
