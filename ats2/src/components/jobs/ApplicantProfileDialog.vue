<template>
  <Dialog 
    v-model="isOpen" 
    :options="{ 
      title: `${applicantProfile?.job_applicant || candidateName || 'Applicant'} Profile`, 
      size: '4xl' 
    }"
  >
    <template #body-content>
      <div v-if="loading" class="profile-loading">
        <div class="text-center py-8 text-gray-500">Loading profile...</div>
      </div>
      <div v-else-if="applicantProfile" class="profile-container">
        <!-- Header Section -->
        <div class="profile-header">
          <div class="profile-avatar-large">
            {{ candidateName?.charAt(0).toUpperCase() }}
          </div>
          <div class="profile-header-info">
            <h2 class="profile-name">{{ applicantProfile.job_applicant || candidateName }}</h2>
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
        </div>

        <!-- Summary Section -->
        <div v-if="applicantProfile.summary" class="profile-section">
          <h3 class="profile-section-title">Summary</h3>
          <p class="profile-summary-text">{{ applicantProfile.summary }}</p>
        </div>

        <!-- Experience Section -->
        <div v-if="applicantProfile.experience?.length" class="profile-section">
          <h3 class="profile-section-title">Experience</h3>
          <div class="profile-timeline">
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
        </div>

        <!-- Education Section -->
        <div v-if="applicantProfile.education?.length" class="profile-section">
          <h3 class="profile-section-title">Education</h3>
          <div class="profile-education-list">
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
        </div>

        <!-- Projects Section -->
        <div v-if="applicantProfile.projects?.length" class="profile-section">
          <h3 class="profile-section-title">Projects</h3>
          <div class="profile-projects-grid">
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
        </div>

        <!-- Skills Section -->
        <div v-if="applicantProfile.skills" class="profile-section">
          <h3 class="profile-section-title">Skills</h3>
          <p class="profile-skills-text">{{ applicantProfile.skills }}</p>
        </div>
      </div>
    </template>
    <template #actions>
      <Button @click="close">Close</Button>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, watch } from 'vue';
import { Dialog, Button } from 'frappe-ui';

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  applicantId: {
    type: String,
    default: null
  },
  candidateName: {
    type: String,
    default: ''
  },
  onFetchProfile: {
    type: Function,
    required: true
  }
});

const emit = defineEmits(['update:modelValue']);

const isOpen = ref(props.modelValue);
const loading = ref(false);
const applicantProfile = ref(null);

watch(() => props.modelValue, (newVal) => {
  isOpen.value = newVal;
  if (newVal && props.applicantId) {
    fetchProfile();
  }
});

watch(isOpen, (newVal) => {
  emit('update:modelValue', newVal);
  if (!newVal) {
    // Reset when closed
    applicantProfile.value = null;
    loading.value = false;
  }
});

async function fetchProfile() {
  if (!props.applicantId) return;
  
  loading.value = true;
  try {
    applicantProfile.value = await props.onFetchProfile(props.applicantId);
  } catch (error) {
    console.error('Failed to load profile:', error);
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

function close() {
  isOpen.value = false;
}
</script>

<style scoped>
.profile-container {
  max-height: 70vh;
  overflow-y: auto;
  padding: 8px;
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
  padding: 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  margin-bottom: 24px;
  color: white;
}

.profile-avatar-large {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  font-weight: 800;
  color: white;
  border: 3px solid rgba(255, 255, 255, 0.3);
}

.profile-header-info {
  flex: 1;
}

.profile-name {
  font-size: 28px;
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
</style>
