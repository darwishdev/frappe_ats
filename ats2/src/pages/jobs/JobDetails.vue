<template>
  <div class="jd-page">
    <!-- Header -->
    <div class="jd-header">
      <div>
        <div class="jd-title-row">
          <h2 class="jd-title">{{ job?.title || 'Job Details' }}</h2>
          <Button size="sm" @click="editJob">Edit</Button>
        </div>
        <div class="jd-subtitle">{{ job?.department }} · {{ job?.work_mode }} · {{ job?.location }}</div>
      </div>

      <div class="jd-header-actions">
        <Button theme="gray" :variant="'solid'" @click="showAddCandidateDialog = true">Add candidates</Button>
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
              {{ allSelected ? 'Deselect All' : 'Select All' }}
            </Button>
            <div v-if="selectedCandidates.size > 0" class="jd-bulk-actions">
              <Button size="sm" theme="gray" :variant="'solid'" @click="showBulkMoveDialog = true">
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
              {{ candidate.name.charAt(0).toUpperCase() }}
            </div>
            <div>
              <div class="jd-item-name">{{ candidate.name }}</div>
              <div class="jd-item-sub">
                via <b>{{ candidate.source }}</b> · {{ formatDate(candidate.created_at) }}
              </div>
            </div>
          </div>
          <div v-if="filteredCandidates.length === 0" class="text-muted" style="padding: 10px">
            No candidates
          </div>
        </div>
      </div>

      <!-- Right: details -->
      <div class="jd-right">
        <div class="jd-detail-card">
          <div v-if="!activeCandidate" class="text-muted">
            Select a candidate from the list.
          </div>
          <div v-else>
            <div class="jd-detail-head">
              <div style="display: flex; align-items: center; gap: 12px">
                <div class="jd-avatar" style="width: 48px; height: 48px; font-size: 20px">
                  {{ activeCandidate.name.charAt(0).toUpperCase() }}
                </div>
                <div>
                  <h3 class="jd-detail-name">{{ activeCandidate.name }}</h3>
                  <div class="jd-detail-meta">
                    {{ activeCandidate.designation || activeCandidate.email }}
                  </div>
                </div>
              </div>

              <div style="display: flex; flex-direction: column; gap: 8px; min-width: 200px">
                <Select
                  v-model="targetStep"
                  :options="stepOptions"
                  placeholder="Select step"
                />
                <Button size="sm" theme="gray" :variant="'solid'" @click="moveCandidateToStep">
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
              <div
                style="
                  margin-top: 16px;
                  padding-top: 16px;
                  border-top: 1px solid var(--border-color, #e6e6e6);
                "
              >
                <Button size="sm" @click="showAssignInterviewDialog = true">
                  📅 Assign Interview
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Candidate Dialog -->
    <Dialog v-model="showAddCandidateDialog" :options="{ title: 'Add Candidate', size: 'lg' }">
      <template #body-content>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1">Name *</label>
            <TextInput
              v-model="newCandidate.name"
              type="text"
              placeholder="Enter candidate name"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Email *</label>
            <TextInput
              v-model="newCandidate.email"
              type="email"
              placeholder="Enter email address"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Phone</label>
            <TextInput
              v-model="newCandidate.phone"
              type="text"
              placeholder="Enter phone number"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Country</label>
            <TextInput
              v-model="newCandidate.country"
              type="text"
              placeholder="Enter country"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Source</label>
            <Select
              v-model="newCandidate.source"
              :options="sourceOptions"
              placeholder="Select source"
            />
          </div>
        </div>
      </template>
      <template #actions>
        <Button @click="showAddCandidateDialog = false">Cancel</Button>
        <Button theme="gray" :variant="'solid'" @click="addCandidate">Add Candidate</Button>
      </template>
    </Dialog>

    <!-- Assign Interview Dialog -->
    <Dialog
      v-model="showAssignInterviewDialog"
      :options="{ title: `Assign Interview to ${activeCandidate?.name || ''}`, size: 'xl' }"
    >
      <template #body-content>
        <div class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium mb-1">Interview Round *</label>
              <Select
                v-model="interviewData.interview_round"
                :options="interviewRoundOptions"
                placeholder="Select round"
              />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">Status *</label>
              <Select
                v-model="interviewData.status"
                :options="interviewStatusOptions"
                placeholder="Select status"
              />
            </div>
          </div>

          <div class="grid grid-cols-3 gap-4">
            <div>
              <label class="block text-sm font-medium mb-1">Scheduled Date *</label>
              <input
                v-model="interviewData.scheduled_on"
                type="date"
                class="form-control"
              />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">From Time *</label>
              <input
                v-model="interviewData.from_time"
                type="time"
                class="form-control"
              />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1">To Time *</label>
              <input
                v-model="interviewData.to_time"
                type="time"
                class="form-control"
              />
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium mb-1">Expected Rating</label>
            <TextInput
              v-model.number="interviewData.expected_average_rating"
              type="number"
              placeholder="0-5"
              min="0"
              max="5"
              step="0.1"
            />
          </div>

          <div>
            <label class="block text-sm font-medium mb-1">Interview Summary</label>
            <textarea
              v-model="interviewData.interview_summary"
              class="form-control"
              rows="3"
              placeholder="Optional notes or summary"
            ></textarea>
          </div>
        </div>
      </template>
      <template #actions>
        <Button @click="showAssignInterviewDialog = false">Cancel</Button>
        <Button theme="gray" :variant="'solid'" @click="assignInterview">Assign Interview</Button>
      </template>
    </Dialog>

    <!-- Bulk Move Dialog -->
    <Dialog v-model="showBulkMoveDialog" :options="{ title: 'Bulk Move Candidates', size: 'md' }">
      <template #body-content>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1">Move to Step *</label>
            <Select
              v-model="bulkMoveData.target_step"
              :options="stepOptions"
              placeholder="Select target step"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Update Status (Optional)</label>
            <Select
              v-model="bulkMoveData.status"
              :options="statusOptions"
              placeholder="Select status"
            />
          </div>
          <p class="text-muted text-sm">Moving {{ selectedCandidates.size }} candidate(s)</p>
        </div>
      </template>
      <template #actions>
        <Button @click="showBulkMoveDialog = false">Cancel</Button>
        <Button theme="primary" @click="bulkMoveCandidates">Move Candidates</Button>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { TextInput, Select, Button, Dialog } from "frappe-ui";
import { JobDetailsAPI } from "../../api/apiClient.js";

const route = useRoute();
const router = useRouter();

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

// Form data
const newCandidate = ref({
  name: "",
  email: "",
  phone: "",
  country: "",
  source: "Campaign",
});

const interviewData = ref({
  interview_round: "HR Screening",
  status: "Scheduled",
  scheduled_on: "",
  from_time: "",
  to_time: "",
  expected_average_rating: 0,
  interview_summary: "",
});

const bulkMoveData = ref({
  target_step: "",
  status: "",
});

// Options for dropdowns
const sourceOptions = [
  { label: "Campaign", value: "Campaign" },
  { label: "LinkedIn", value: "LinkedIn" },
  { label: "Referral", value: "Referral" },
  { label: "Direct", value: "Direct" },
  { label: "Other", value: "Other" },
];

const interviewRoundOptions = [
  { label: "HR Screening", value: "HR Screening" },
  { label: "Technical Screening", value: "Technical Screening" },
  { label: "Technical Interview", value: "Technical Interview" },
  { label: "Manager Round", value: "Manager Round" },
  { label: "Final Round", value: "Final Round" },
  { label: "Cultural Fit", value: "Cultural Fit" },
];

const interviewStatusOptions = [
  { label: "Pending", value: "Pending" },
  { label: "Scheduled", value: "Scheduled" },
  { label: "Completed", value: "Completed" },
  { label: "Cleared", value: "Cleared" },
  { label: "Rejected", value: "Rejected" },
  { label: "Cancelled", value: "Cancelled" },
];

const statusOptions = [
  { label: "No Change", value: "" },
  { label: "Open", value: "Open" },
  { label: "Hold", value: "Hold" },
  { label: "Rejected", value: "Rejected" },
  { label: "Hired", value: "Hired" },
];

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
          const existingIdx = allCandidates.findIndex(
            (c) => c.id === candidate["applicant_email,"]
          );
          if (existingIdx === -1) {
            allCandidates.push({
              id: candidate["applicant_email,"],
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
  console.log("Edit job:", job.value?.name);
  // You can implement routing to edit page here
}

async function addCandidate() {
  if (!newCandidate.value.name || !newCandidate.value.email) {
    alert("Please fill in required fields");
    return;
  }

  try {
    await JobDetailsAPI.addCandidate(job.value.name, {
      candidate_name: newCandidate.value.name,
      candidate_email: newCandidate.value.email,
      phone: newCandidate.value.phone,
      country: newCandidate.value.country,
      source: newCandidate.value.source,
    });

    alert("Candidate added successfully");
    showAddCandidateDialog.value = false;

    // Reset form
    newCandidate.value = {
      name: "",
      email: "",
      phone: "",
      country: "",
      source: "Campaign",
    };

    // Reload data
    await loadJobDetails();
  } catch (error) {
    alert(`Error: ${error.message}`);
  }
}

async function moveCandidateToStep() {
  if (!activeCandidate.value || !targetStep.value) return;

  if (targetStep.value === activeCandidate.value.stage) {
    alert("Candidate is already in this stage");
    return;
  }

  const targetStepName =
    job.value.steps.find((s) => s.key === targetStep.value)?.label || targetStep.value;

  try {
    const response = await JobDetailsAPI.moveCandidateToStep(
      activeCandidate.value.id,
      job.value.name,
      targetStep.value
    );

    if (response.success) {
      alert(`${activeCandidate.value.name} moved to "${targetStepName}"`);

      // Update local state
      const candidate = candidates.value.find((c) => c.id === activeCandidate.value.id);
      if (candidate) {
        candidate.stage = targetStep.value;
        candidate.stage_name = targetStepName;
      }
    } else {
      alert(`Error: ${response.message}`);
    }
  } catch (error) {
    alert(`Error: ${error.message}`);
  }
}

async function assignInterview() {
  if (
    !interviewData.value.interview_round ||
    !interviewData.value.status ||
    !interviewData.value.scheduled_on ||
    !interviewData.value.from_time ||
    !interviewData.value.to_time
  ) {
    alert("Please fill in all required fields");
    return;
  }

  if (interviewData.value.from_time >= interviewData.value.to_time) {
    alert("End time must be after start time");
    return;
  }

  // Mock implementation - log the data
  console.log("Assigning interview:", {
    ...interviewData.value,
    candidate: activeCandidate.value?.email,
    job: job.value?.name,
  });

  alert(
    `Interview assigned to ${activeCandidate.value?.name} on ${interviewData.value.scheduled_on}`
  );
  showAssignInterviewDialog.value = false;

  // Reset form
  interviewData.value = {
    interview_round: "HR Screening",
    status: "Scheduled",
    scheduled_on: "",
    from_time: "",
    to_time: "",
    expected_average_rating: 0,
    interview_summary: "",
  };
}

async function bulkMoveCandidates() {
  if (!bulkMoveData.value.target_step) {
    alert("Please select a target step");
    return;
  }

  const targetStepLabel =
    job.value.steps.find((s) => s.key === bulkMoveData.value.target_step)?.label || "";

  const payload = {
    names: Array.from(selectedCandidates.value),
    pipeline_step: bulkMoveData.value.target_step,
  };

  if (bulkMoveData.value.status) {
    payload.status = bulkMoveData.value.status;
  }

  try {
    const response = await JobDetailsAPI.bulkUpdateApplicants(payload);

    if (response.success) {
      alert(`${response.updated_count} candidate(s) moved to "${targetStepLabel}"`);

      // Update local state
      selectedCandidates.value.forEach((candidateId) => {
        const candidate = candidates.value.find((c) => c.id === candidateId);
        if (candidate) {
          candidate.stage = bulkMoveData.value.target_step;
          candidate.stage_name = targetStepLabel;
          if (bulkMoveData.value.status) {
            candidate.status = bulkMoveData.value.status;
          }
        }
      });

      clearSelection();
      showBulkMoveDialog.value = false;

      // Reset form
      bulkMoveData.value = {
        target_step: "",
        status: "",
      };
    } else {
      alert(`Error: ${response.message}`);
    }
  } catch (error) {
    alert(`Error: ${error.message}`);
  }
}

async function loadJobDetails() {
  try {
    const jobId = route.params.jobId || route.query.job || "HR-OPN-2026-0002";
    const rawJob = await JobDetailsAPI.fetchJobDetails(jobId);
    const transformedData = transformJobData(rawJob);

    job.value = transformedData;
    candidates.value = transformedData.candidates;
    activeStep.value = "all";
    activeCandidateId.value = candidates.value[0]?.id || null;

    if (activeCandidate.value) {
      targetStep.value = activeCandidate.value.stage;
    }
  } catch (error) {
    alert(`Error loading job details: ${error.message}`);
  }
}

// Watch for search query changes
watch(searchQuery, () => {
  if (!filteredCandidates.value.some((c) => c.id === activeCandidateId.value)) {
    activeCandidateId.value = filteredCandidates.value[0]?.id || null;
  }
});

// Load data on mount
onMounted(() => {
  loadJobDetails();
});
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
  grid-template-columns: 360px 1fr;
  gap: 14px;
  min-height: 520px;
}

.jd-left,
.jd-right {
  background: #ffffff66;
  border: 1px solid var(--border-color, #e6e6e6);
  border-radius: 10px;
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
  margin-top: 6px;
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
