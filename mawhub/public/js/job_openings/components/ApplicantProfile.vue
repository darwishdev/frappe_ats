<template>
  <div class="applicant-profile">
    <!-- Progress Bar -->
    <div v-if="showProgress" class="progress-bar-container">
      <div class="progress-bar-header">
        <span class="progress-bar-label">Parsing Resume</span>
        <span class="progress-bar-percentage">{{ progressPercentage }}%</span>
      </div>
      <div class="progress-bar-track">
        <div
          class="progress-bar-fill"
          :style="{ width: progressPercentage + '%' }"
        ></div>
      </div>
      <div class="progress-bar-steps">
        <div
          v-for="step in 5"
          :key="step"
          :class="['progress-step', { active: parsingProgress >= step }]"
        >
          <div class="progress-step-dot"></div>
          <span class="progress-step-label">Step {{ step }}</span>
        </div>
      </div>
    </div>

    <div
      v-if="loading && !applicantProfile"
      class="profile-loading"
    >
      <div style="text-align: center; padding: 40px; color: #888;">
        Loading profile...
      </div>
    </div>
    <div
      v-else-if="applicantProfile"
      class="profile-container"
    >
      <!-- Personal Information Section -->
      <div class="profile-section">
        <h3 class="profile-section-title">
          Personal Information
        </h3>
        <div class="profile-personal-grid">
          <!-- <div
            v-if="applicantProfile.name"
            class="profile-personal-item"
          >
            <span class="profile-personal-icon">🆔</span>
            <div>
              <div class="profile-personal-label">
                ID
              </div>
              <div class="profile-personal-value">
                {{ applicantProfile.name }}
              </div>
            </div>
          </div> -->
          <div
            v-if="applicantProfile.email"
            class="profile-personal-item"
          >
            <span class="profile-personal-icon">📧</span>
            <div>
              <div class="profile-personal-label">
                Email
              </div>
              <div class="profile-personal-value">
                {{ applicantProfile.email }}
              </div>
            </div>
          </div>
          <div
            v-if="applicantProfile.phone"
            class="profile-personal-item"
          >
            <span class="profile-personal-icon">📱</span>
            <div>
              <div class="profile-personal-label">
                Phone
              </div>
              <div class="profile-personal-value">
                {{ applicantProfile.phone }}
              </div>
            </div>
          </div>
          <div
            v-if="applicantProfile.location"
            class="profile-personal-item"
          >
            <span class="profile-personal-icon">📍</span>
            <div>
              <div class="profile-personal-label">
                Location
              </div>
              <div class="profile-personal-value">
                {{ applicantProfile.location }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Metadata Section -->
      <!-- <div
        v-if="applicantProfile?.creation || applicantProfile?.modified || applicantProfile?.owner"
        class="profile-section"
      >
        <h3 class="profile-section-title">
          Document Information
        </h3>
        <div class="profile-personal-grid">
          <div
            v-if="applicantProfile.owner"
            class="profile-personal-item"
          >
            <span class="profile-personal-icon">👨‍💼</span>
            <div>
              <div class="profile-personal-label">
                Owner
              </div>
              <div class="profile-personal-value">
                {{ applicantProfile.owner }}
              </div>
            </div>
          </div>
          <div
            v-if="applicantProfile.creation"
            class="profile-personal-item"
          >
            <span class="profile-personal-icon">📅</span>
            <div>
              <div class="profile-personal-label">
                Created
              </div>
              <div class="profile-personal-value">
                {{ formatDateTime(applicantProfile.creation) }}
              </div>
            </div>
          </div>
          <div
            v-if="applicantProfile.modified"
            class="profile-personal-item"
          >
            <span class="profile-personal-icon">🔄</span>
            <div>
              <div class="profile-personal-label">
                Modified
              </div>
              <div class="profile-personal-value">
                {{ formatDateTime(applicantProfile.modified) }}
              </div>
            </div>
          </div>
          <div
            v-if="applicantProfile.modified_by"
            class="profile-personal-item"
          >
            <span class="profile-personal-icon">✏️</span>
            <div>
              <div class="profile-personal-label">
                Modified By
              </div>
              <div class="profile-personal-value">
                {{ applicantProfile.modified_by }}
              </div>
            </div>
          </div>
          <div
            v-if="applicantProfile.file_path"
            class="profile-personal-item"
          >
            <span class="profile-personal-icon">📄</span>
            <div>
              <div class="profile-personal-label">
                File Path
              </div>
              <div class="profile-personal-value profile-file-path">
                {{ applicantProfile.file_path }}
              </div>
            </div>
          </div>
          <div
            v-if="applicantProfile.file_hash"
            class="profile-personal-item"
          >
            <span class="profile-personal-icon">🔐</span>
            <div>
              <div class="profile-personal-label">
                File Hash
              </div>
              <div class="profile-personal-value profile-file-hash">
                {{ applicantProfile.file_hash }}
              </div>
            </div>
          </div>
        </div>
      </div> -->

      <!-- Summary Section -->
      <div
        v-if="applicantProfile?.summary"
        class="profile-section"
      >
        <h3 class="profile-section-title">
          Summary
        </h3>
        <p v-if="typeof applicantProfile.summary === 'string'" class="profile-summary-text">
          {{ applicantProfile.summary }}
        </p>
        <p v-if="typeof applicantProfile.summary === 'object'" class="profile-summary-text">
          {{ applicantProfile.summary.summary }}
        </p>
      </div>

      <!-- Skills Section -->
      <div
        v-if="applicantProfile?.skills"
        class="profile-section"
      >
        <h3 class="profile-section-title">
          Skills
        </h3>
        <div
          v-if="typeof applicantProfile.skills === 'string'"
          class="profile-skills-text"
        >
          {{ applicantProfile.skills }}
        </div>
        <div
          v-else-if="Array.isArray(applicantProfile.skills)"
          class="profile-skills-grid"
        >
          <span
            v-for="(skill, index) in applicantProfile.skills"
            :key="index"
            class="profile-skill-badge"
          >
            {{ skill }}
          </span>
        </div>
      </div>

      <!-- Experience Section -->
      <div
        v-if="applicantProfile?.experience && applicantProfile.experience.length > 0"
        class="profile-section"
      >
        <h3 class="profile-section-title">
          Experience
        </h3>
        <div class="profile-timeline">
          <div
            v-for="(exp, index) in applicantProfile.experience"
            :key="index"
            class="profile-timeline-item"
          >
            <div class="profile-timeline-dot" />
            <div class="profile-timeline-content">
              <div class="profile-exp-header">
                <div>
                  <h4 class="profile-exp-role">
                    {{ exp.role || exp.title }}
                  </h4>
                  <p class="profile-exp-company">
                    {{ exp.company }}
                  </p>
                </div>
                <span class="profile-exp-duration">
                  {{ formatProfileDate(exp.from_date || exp.start_date) }} - {{ formatProfileDate(exp.to_date || exp.end_date) }}
                </span>
              </div>
              <div v-if="exp.responsibilities || exp.description">
                <ul v-if="splitBulletPoints(exp.responsibilities || exp.description)" class="profile-exp-description-list">
                  <li v-for="(point, idx) in splitBulletPoints(exp.responsibilities || exp.description)" :key="idx">
                    {{ point }}
                  </li>
                </ul>
                <p v-else class="profile-exp-description">
                  {{ exp.responsibilities || exp.description }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Education Section -->
      <div
        v-if="applicantProfile?.education && applicantProfile.education.length > 0"
        class="profile-section"
      >
        <h3 class="profile-section-title">
          Education
        </h3>
        <div class="profile-timeline">
          <div
            v-for="(edu, index) in applicantProfile.education"
            :key="index"
            class="profile-timeline-item"
          >
            <div class="profile-timeline-dot" />
            <div class="profile-timeline-content">
              <div class="profile-exp-header">
                <div>
                  <h4 class="profile-exp-role">
                    {{ edu.degree }}
                  </h4>
                  <p class="profile-exp-company">
                    {{ edu.institution }}
                  </p>
                </div>
                <span class="profile-exp-duration">
                  {{ formatProfileDate(edu.from_date || edu.start_date) }} - {{ formatProfileDate(edu.to_date || edu.end_date) }}
                </span>
              </div>
              <div v-if="edu.description">
                <ul v-if="splitBulletPoints(edu.description)" class="profile-exp-description-list">
                  <li v-for="(point, idx) in splitBulletPoints(edu.description)" :key="idx">
                    {{ point }}
                  </li>
                </ul>
                <p v-else class="profile-exp-description">
                  {{ edu.description }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Projects Section -->
      <div
        v-if="applicantProfile?.projects && applicantProfile.projects.length > 0"
        class="profile-section"
      >
        <h3 class="profile-section-title">
          Projects
        </h3>
        <div class="profile-projects-grid">
          <div
            v-for="(project, index) in applicantProfile.projects.filter((p) => p.description || p.title)"
            :key="index"
            class="profile-project-card"
          >
            <div class="profile-project-header">
              <h4 class="profile-project-name">
                {{ project.name || project.title }}
              </h4>
              <a
                v-if="project.url || project.link"
                :href="project.url || project.link"
                target="_blank"
                class="profile-project-link"
              >
                🔗
              </a>
            </div>
            <p
              v-if="project.description"
              class="profile-project-description"
            >
              {{ project.description }}
            </p>
          </div>
        </div>
      </div>

      <!-- Links Section -->
      <div
        v-if="applicantProfile?.links && applicantProfile.links.length > 0"
        class="profile-section"
      >
        <h3 class="profile-section-title">
          Links
        </h3>
        <div class="profile-links-grid">
          <a
            v-for="(link, index) in applicantProfile.links"
            :key="index"
            :href="link.url"
            target="_blank"
            class="profile-link-item"
          >
            {{ link.label || link.url }}
          </a>
        </div>
      </div>
    </div>
    <div
      v-else
      class="profile-empty"
    >
      <p class="profile-empty-state">
        No profile data available for this candidate
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed, getCurrentInstance } from 'vue';

const { proxy } = getCurrentInstance();
const frappe = proxy.$frappe;

const props = defineProps({
  candidate: {
    type: Object,
    default: null
  },
  jobId: {
    type: String,
    required: true
  },
  frappe: {
    type: Object,
    default: null
  },
  channelName: {
    type: String,
    default: null
  }
});

const loading = ref(false);
const applicantProfile = ref(null);
const parsingProgress = ref(0);
const showProgress = ref(false);

// Computed property for progress percentage
const progressPercentage = computed(() => {
  return Math.round((parsingProgress.value / 5) * 100);
});

// Setup realtime listener if provided
if (props.frappe && props.channelName) {
  applicantProfile.value = {};
  showProgress.value = true;
  props.frappe.realtime.on(props.channelName, (response) => {
    console.log('ApplicantProfile received realtime update:', response);

    if (response.event === 'update' && response.data && response.data.content) {
      // Increment progress
      parsingProgress.value++;

      // Update the applicant profile with the parsed data
      // Merge or update the applicantProfile with new data
        if(response.data.name == 'personal'){
          applicantProfile.value = {
            ...applicantProfile.value,
            ...response.data.content
          }
          console.log(applicantProfile.value , 'from personal');

        }
        else{
          applicantProfile.value[response.data.name] = response.data.content
        }
        console.log(applicantProfile.value , 'from global');
    }
    if(response.event === 'final') {
      parsingProgress.value = 5; // Mark as complete
      // showProgress.value = false; // Hide progress bar after completion
    }
  });
}

// Watch for candidate changes and fetch profile
watch(
  () => props.candidate,
  async (newCandidate) => {
    if (newCandidate?.job_applicant) {
      await fetchApplicantProfile(newCandidate.job_applicant);
    }
  },
  { immediate: true }
);

async function fetchApplicantProfile(applicantId) {
  if (!applicantId) return;

  loading.value = true;

  frappe.call({
    method: "mawhub.api.applicant_job_applicant_api.job_applicant_find",
    type: "GET",
    args: {
      job: props.jobId,
      name: applicantId
    },
    callback: function(res) {
      loading.value = false;
      if (res.message) {
        applicantProfile.value = res.message.resume || null;
      }
    },
    error: function(err) {
      loading.value = false;
      console.error('Failed to load applicant profile:', err);
      applicantProfile.value = null;
      frappe.msgprint({
        title: 'Error',
        message: 'Failed to load applicant profile',
        indicator: 'red'
      });
    }
  });
}

function formatProfileDate(dateStr) {
  if (!dateStr) return 'Present';
  try {
    // const date = new Date(dateStr);
    // return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short' });
    return dateStr
  } catch {
    return dateStr;
  }
}

function formatDateTime(dateTimeStr) {
  if (!dateTimeStr) return '';
  try {
    const date = new Date(dateTimeStr);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch {
    return dateTimeStr;
  }
}

function splitBulletPoints(text) {
  if (!text) return null;
  
  // Check if text contains bullet points (●)
  if (text.includes('●')) {
    // Split by bullet point and filter out empty strings
    return text
      .split('●')
      .map(item => item.trim())
      .filter(item => item.length > 0);
  }
  
  return null;
}
</script>

<style scoped>
.applicant-profile {
  padding: 0;
}

.profile-container {
  max-height: calc(100vh - 400px);
  padding: 8px;
  overflow-y: auto;
}

.profile-loading,
.profile-empty {
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.profile-section {
  margin-bottom: 18px;
}

.profile-section-title {
  font-size: 20px;
  font-weight: 700;
  color: #111827;
  margin: 0 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid #e5e7eb;
}

.profile-summary-text {
  padding: 10px;
  border-radius: 10px;
  font-size: 15px;
  line-height: 1.7;
  color: #374151;
  margin: 0;
}

.profile-personal-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.profile-personal-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.profile-personal-icon {
  font-size: 24px;
  line-height: 1;
}

.profile-personal-label {
  font-size: 12px;
  color: #6b7280;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}

.profile-personal-value {
  font-size: 15px;
  color: #111827;
  font-weight: 600;
}

.profile-file-path,
.profile-file-hash {
  word-break: break-all;
  font-size: 13px;
  font-weight: 500;
}

.profile-file-hash {
  font-family: monospace;
}

.profile-skills-text {
  font-size: 14px;
  line-height: 1.7;
  color: #374151;
  margin: 0;
  background: #f9fafb;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.profile-skills-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.profile-skill-badge {
  display: inline-block;
  font-size: 13px;
  font-weight: 500;
  color: #374151;
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 6px 12px;
  transition: all 0.2s;
}

.profile-skill-badge:hover {
  background: #e5e7eb;
  border-color: #d1d5db;
  transform: translateY(-1px);
}

.profile-timeline {
  position: relative;
  padding-left: 32px;
}

.profile-timeline::before {
  content: '';
  position: absolute;
  left: 8px;
  top: 8px;
  bottom: 8px;
  width: 2px;
  background: #e5e7eb;
}

.profile-timeline-item {
  position: relative;
  margin-bottom: 24px;
}

.profile-timeline-dot {
  position: absolute;
  left: -28px;
  top: 6px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #667eea;
  border: 3px solid white;
  box-shadow: 0 0 0 2px #667eea;
}

.profile-timeline-content {
  background: #f9fafb;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #e5e7eb;
}

.profile-exp-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 12px;
}

.profile-exp-role {
  font-size: 18px;
  font-weight: 700;
  color: #000000;
  margin: 0 0 4px 0;
}

.profile-exp-company {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}

.profile-exp-duration {
  font-size: 13px;
  color: #9ca3af;
  font-weight: 500;
  white-space: nowrap;
}

.profile-exp-description {
  font-size: 14px;
  line-height: 1.6;
  color: #4b5563;
  margin: 0;
}

.profile-exp-description-list {
  font-size: 14px;
  line-height: 1.6;
  color: #4b5563;
  margin: 0;
  padding-left: 20px;
  list-style-type: disc;
}

.profile-exp-description-list li {
  margin-bottom: 8px;
}

.profile-exp-description-list li:last-child {
  margin-bottom: 0;
}

.profile-projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.profile-project-card {
  background: #f9fafb;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #e5e7eb;
  transition: all 0.2s;
}

.profile-project-card:hover {
  border-color: #d1d5db;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.profile-project-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.profile-project-name {
  font-size: 16px;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

.profile-project-link {
  font-size: 18px;
  text-decoration: none;
  opacity: 0.6;
  transition: opacity 0.2s;
}

.profile-project-link:hover {
  opacity: 1;
}

.profile-project-description {
  font-size: 14px;
  line-height: 1.6;
  color: #4b5563;
  margin: 0;
}

.profile-links-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.profile-link-item {
  display: inline-block;
  font-size: 14px;
  color: #667eea;
  text-decoration: none;
  padding: 8px 16px;
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  transition: all 0.2s;
}

.profile-link-item:hover {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

.profile-empty-state {
  font-size: 14px;
  color: #9ca3af;
  text-align: center;
  padding: 24px;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  margin: 0;
}

/* Dark Mode Styles */
[data-theme="dark"] .profile-section-title {
  color: #f0f0f0;
  border-bottom-color: #3a3a3a;
}

[data-theme="dark"] .profile-summary-text,
[data-theme="dark"] .profile-skills-text {
  color: #d1d5db;
  background: #2a2a2a;
  border-color: #3a3a3a;
}

[data-theme="dark"] .profile-personal-item {
  background: #2a2a2a;
  border-color: #3a3a3a;
}

[data-theme="dark"] .profile-personal-label {
  color: #9ca3af;
}

[data-theme="dark"] .profile-personal-value {
  color: #f0f0f0;
}

[data-theme="dark"] .profile-file-path,
[data-theme="dark"] .profile-file-hash {
  color: #d1d5db;
}

[data-theme="dark"] .profile-skill-badge {
  color: #e0e0e0;
  background: #333;
  border-color: #3a3a3a;
}

[data-theme="dark"] .profile-skill-badge:hover {
  background: #3a3a3a;
  border-color: #444;
}

[data-theme="dark"] .profile-timeline::before {
  background: #3a3a3a;
}

[data-theme="dark"] .profile-timeline-dot {
  background: #667eea;
  border-color: #2a2a2a;
  box-shadow: 0 0 0 2px #667eea;
}

[data-theme="dark"] .profile-timeline-content {
  background: #2a2a2a;
  border-color: #3a3a3a;
}

[data-theme="dark"] .profile-exp-role {
  color: #f0f0f0;
}

[data-theme="dark"] .profile-exp-company {
  color: #9ca3af;
}

[data-theme="dark"] .profile-exp-duration {
  color: #6b7280;
}

[data-theme="dark"] .profile-exp-description {
  color: #d1d5db;
}

[data-theme="dark"] .profile-exp-description-list {
  color: #d1d5db;
}

[data-theme="dark"] .profile-project-card {
  background: #2a2a2a;
  border-color: #3a3a3a;
}

[data-theme="dark"] .profile-project-card:hover {
  border-color: #444;
}

[data-theme="dark"] .profile-project-name {
  color: #f0f0f0;
}

[data-theme="dark"] .profile-project-description {
  color: #d1d5db;
}

[data-theme="dark"] .profile-link-item {
  color: #8b9dff;
  background: #333;
  border-color: #3a3a3a;
}

[data-theme="dark"] .profile-link-item:hover {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

[data-theme="dark"] .profile-empty-state {
  color: #6b7280;
  background: #2a2a2a;
  border-color: #3a3a3a;
}

[data-theme="dark"] .profile-loading,
[data-theme="dark"] .profile-empty {
  color: #9ca3af;
}

/* Progress Bar Styles */
.progress-bar-container {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.progress-bar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.progress-bar-label {
  font-size: 16px;
  font-weight: 600;
  color: white;
  letter-spacing: 0.3px;
}

.progress-bar-percentage {
  font-size: 24px;
  font-weight: 700;
  color: white;
  font-variant-numeric: tabular-nums;
}

.progress-bar-track {
  width: 100%;
  height: 12px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  overflow: hidden;
  position: relative;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #ffffff 0%, #f0f0f0 100%);
  border-radius: 6px;
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(255, 255, 255, 0.3);
  position: relative;
  overflow: hidden;
}

.progress-bar-fill::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  right: 0;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.4),
    transparent
  );
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

.progress-bar-steps {
  display: flex;
  justify-content: space-between;
  margin-top: 16px;
  gap: 8px;
}

.progress-step {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.progress-step-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  border: 2px solid rgba(255, 255, 255, 0.5);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.progress-step.active .progress-step-dot {
  background: white;
  border-color: white;
  box-shadow: 0 0 12px rgba(255, 255, 255, 0.8);
  transform: scale(1.2);
}

.progress-step-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 500;
  transition: all 0.3s ease;
}

.progress-step.active .progress-step-label {
  color: white;
  font-weight: 600;
}

/* Dark Mode Progress Bar */
[data-theme="dark"] .progress-bar-container {
  background: linear-gradient(135deg, #4c5fd7 0%, #5a3d7a 100%);
}
</style>
