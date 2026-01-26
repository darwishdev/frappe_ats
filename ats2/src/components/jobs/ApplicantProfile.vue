<template>
  <div class="applicant-profile">
    <div v-if="loading && !applicantProfile" class="profile-loading">
      <div class="text-center py-8 text-gray-500">Loading profile...</div>
    </div>
    <div v-else-if="applicantProfile" class="profile-container">
      <!-- Header Section -->
      <!-- <div class="profile-header">
        <div class="profile-avatar-large">
          {{ applicantProfile?.name?.charAt(0).toUpperCase() || applicantProfile.applicant_name?.charAt(0).toUpperCase() }}
        </div>
        <div class="profile-header-info">
          <h2 class="profile-name">{{ applicantProfile?.name || applicantProfile.applicant_name }}</h2>
          <div class="profile-contact-links">
            <a
              v-for="link in applicantProfile.links"
              :key="link.url"
              :href="link.url"
              target="_blank"
              class="profile-link"
            >
              {{ link.label }}
            </a>
          </div>
        </div>
      </div> -->

      <!-- Personal Information Section -->
      <div class="profile-section">
        <h3 class="profile-section-title">Personal Information</h3>
        <div v-if="applicantProfile?.personal" class="profile-personal-grid">
          <div v-if="applicantProfile.personal.name" class="profile-personal-item">
            <span class="profile-personal-icon">👤</span>
            <div>
              <div class="profile-personal-label">Name</div>
              <div class="profile-personal-value">{{ applicantProfile.personal.name }}</div>
            </div>
          </div>
          <div v-if="applicantProfile.personal.email" class="profile-personal-item">
            <span class="profile-personal-icon">📧</span>
            <div>
              <div class="profile-personal-label">Email</div>
              <div class="profile-personal-value">{{ applicantProfile.personal.email }}</div>
            </div>
          </div>
          <div v-if="applicantProfile.personal.phone" class="profile-personal-item">
            <span class="profile-personal-icon">📱</span>
            <div>
              <div class="profile-personal-label">Phone</div>
              <div class="profile-personal-value">{{ applicantProfile.personal.phone }}</div>
            </div>
          </div>
          <div v-if="applicantProfile.personal.location" class="profile-personal-item">
            <span class="profile-personal-icon">📍</span>
            <div>
              <div class="profile-personal-label">Location</div>
              <div class="profile-personal-value">{{ applicantProfile.personal.location }}</div>
            </div>
          </div>
        </div>
        <p v-else class="profile-empty-state">No personal information available</p>
      </div>

      <!-- Summary Section -->
      <div class="profile-section">
        <h3 class="profile-section-title">Summary</h3>
        <p v-if="applicantProfile.summary" class="profile-summary-text">{{ applicantProfile.summary }}</p>
        <p v-else class="profile-empty-state">No summary available</p>
      </div>

      <!-- Experience Section -->
      <div class="profile-section">
        <h3 class="profile-section-title">Experience</h3>
        <div v-if="applicantProfile.experience?.length" class="profile-timeline">
          <div
            v-for="(exp, idx) in applicantProfile.experience"
            :key="idx"
            class="profile-timeline-item"
          >
            <div class="profile-timeline-dot"></div>
            <div class="profile-timeline-content">
              <div class="profile-exp-header">
                <div>
                  <h4 class="profile-exp-role">{{ exp.role }}</h4>
                  <div class="profile-exp-company">{{ exp.company }}</div>
                </div>
                <div class="profile-exp-duration">
                  {{ formatProfileDate(exp.from_date) }} - {{ formatProfileDate(exp.to_date) }}
                </div>
              </div>
              <p class="profile-exp-description" v-if="exp.description">{{ exp.description }}</p>
            </div>
          </div>
        </div>
        <p v-else class="profile-empty-state">No experience available</p>
      </div>

      <!-- Education Section -->
      <div class="profile-section">
        <h3 class="profile-section-title">Education</h3>
        <div v-if="applicantProfile.education?.length" class="profile-education-list">
          <div
            v-for="(edu, idx) in applicantProfile.education"
            :key="idx"
            class="profile-education-item"
          >
            <div class="profile-edu-icon">🎓</div>
            <div>
              <h4 class="profile-edu-degree">{{ edu.degree }}</h4>
              <div class="profile-edu-institution">{{ edu.institution }}</div>
              <div class="profile-edu-duration">
                {{ formatProfileDate(edu.from_date) }} - {{ formatProfileDate(edu.to_date) }}
              </div>
            </div>
          </div>
        </div>
        <p v-else class="profile-empty-state">No education available</p>
      </div>

      <!-- Projects Section -->
      <div class="profile-section">
        <h3 class="profile-section-title">Projects</h3>
        <div v-if="applicantProfile.projects?.length" class="profile-projects-grid">
          <div
            v-for="(project, idx) in applicantProfile.projects"
            :key="idx"
            class="profile-project-card"
          >
            <div class="profile-project-header">
              <h4 class="profile-project-title">{{ project.title }}</h4>
              <a
                v-if="project.link"
                :href="project.link"
                target="_blank"
                class="profile-project-link"
              >
                🔗
              </a>
            </div>
            <p class="profile-project-description">{{ project.description }}</p>
          </div>
        </div>
        <p v-else class="profile-empty-state">No projects available</p>
      </div>

      <!-- Skills Section -->
      <div class="profile-section">
        <h3 class="profile-section-title">Skills</h3>
        <div v-if="applicantProfile?.skills && Array.isArray(applicantProfile.skills) && applicantProfile.skills.length > 0" class="profile-skills-grid">
          <span
            v-for="(skill, idx) in applicantProfile.skills"
            :key="idx"
            class="profile-skill-badge"
          >
            {{ skill }}
          </span>
        </div>
        <div v-else-if="applicantProfile?.skills && typeof applicantProfile.skills === 'string'" class="profile-skills-grid">
          <span
            v-for="(skill, idx) in applicantProfile.skills.split(',').map(s => s.trim())"
            :key="idx"
            class="profile-skill-badge"
          >
            {{ skill }}
          </span>
        </div>
        <p v-else class="profile-empty-state">No skills available</p>
      </div>
    </div>
    <div v-else class="text-muted text-center py-8">
      Select a candidate from the list.
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import { createResource } from "frappe-ui";
import { JobDetailsAPI } from "../../api/apiClient.js";

const props = defineProps({
  candidate: {
    type: Object,
    default: null,
  },
});

JobDetailsAPI.init(createResource);

const loading = ref(false);
const applicantProfile = ref(null);

// Watch for candidate changes and fetch profile
watch(
  () => props.candidate,
  async (newCandidate) => {
    if (newCandidate?.id) {
      await fetchApplicantProfile(newCandidate.id);
    } else {
      applicantProfile.value = null;
    }
  },
  { immediate: true }
);

async function fetchApplicantProfile(applicantId) {
  if (!applicantId) return;
  
  loading.value = true;
  try {
    const profile = await JobDetailsAPI.jobApplicantFind(applicantId);
    applicantProfile.value = profile?.resume || null;
  } catch (error) {
    console.error('Failed to load applicant profile:', error);
    applicantProfile.value = null;
  } finally {
    loading.value = false;
  }
}

function formatProfileDate(dateStr) {
  if (!dateStr) return 'Present';
  try {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short' });
  } catch {
    return dateStr;
  }
}
</script>

<style scoped>
.applicant-profile {
  padding: 0;
}

.profile-container {
  max-height: calc(100vh - 480px);
  padding: 8px;
  overflow-y: auto;
}

.profile-loading {
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 15px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  margin-bottom: 24px;
  color: white;
}

.profile-avatar-large {
  width: 65px;
  height: 65px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 30px;
  font-weight: 800;
  color: white;
  border: 3px solid rgba(255, 255, 255, 0.3);
}

.profile-header-info {
  flex: 1;
}

.profile-name {
  font-size: 24px;
  font-weight: 800;
  margin: 0 0 8px 0;
  color: white;
}

.profile-contact-links {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.profile-link {
  color: rgba(255, 255, 255, 0.9);
  text-decoration: none;
  font-size: 14px;
  padding: 4px 12px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 20px;
  transition: all 0.2s;
}

.profile-link:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-1px);
}

.profile-section {
  margin-bottom: 32px;
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
  font-size: 15px;
  line-height: 1.7;
  color: #374151;
  margin: 0;
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
  color: #111827;
  margin: 0 0 4px 0;
}

.profile-exp-company {
  font-size: 15px;
  font-weight: 600;
  color: #667eea;
}

.profile-exp-duration {
  font-size: 13px;
  color: #6b7280;
  white-space: nowrap;
  background: white;
  padding: 4px 12px;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
}

.profile-exp-description {
  font-size: 14px;
  line-height: 1.6;
  color: #4b5563;
  margin: 0;
  white-space: pre-line;
}

.profile-education-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.profile-education-item {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.profile-edu-icon {
  font-size: 32px;
  line-height: 1;
}

.profile-edu-degree {
  font-size: 16px;
  font-weight: 700;
  color: #111827;
  margin: 0 0 4px 0;
}

.profile-edu-institution {
  font-size: 15px;
  font-weight: 600;
  color: #667eea;
  margin-bottom: 4px;
}

.profile-edu-duration {
  font-size: 13px;
  color: #6b7280;
}

.profile-projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.profile-project-card {
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  transition: all 0.2s;
}

.profile-project-card:hover {
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
  transform: translateY(-2px);
}

.profile-project-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.profile-project-title {
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
</style>
