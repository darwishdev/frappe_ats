<template>
  <div class="applicant-resume">
    <div
      v-if="loading && !resumeData"
      class="resume-loading"
    >
      <div style="text-align: center; padding: 40px; color: #888;">
        Loading resume...
      </div>
    </div>
    <div
      v-else-if="resumeData?.file_path"
      class="resume-container"
    >
      <!-- <div class="resume-header">
        <div class="resume-info">
          <span class="resume-icon">📄</span>
          <div>
            <div class="resume-filename">
              {{ getFileName(resumeData.file_path) }}
            </div>
            <div class="resume-meta">
              {{ resumeData.file_path }}
            </div>
          </div>
        </div>
        <a
          :href="getFileUrl(resumeData.file_path)"
          target="_blank"
          class="btn btn-sm btn-default resume-download-btn"
        >
          <span class="fa fa-download"></span> Download
        </a>
      </div> -->
      <div class="resume-viewer">
        <embed
          :src="getFileUrl(resumeData.file_path)"
          type="application/pdf"
          class="resume-pdf-embed"
        />
      </div>
    </div>
    <div
      v-else
      class="resume-empty"
    >
      <div class="resume-empty-state">
        <span class="fa fa-file-pdf-o" style="font-size: 48px; color: #d1d5db; margin-bottom: 16px;"></span>
        <p class="resume-empty-text">
          No resume file available for this candidate
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, getCurrentInstance } from 'vue';

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
  }
});

const loading = ref(false);
const resumeData = ref(null);

// Watch for candidate changes and fetch resume data
watch(
  () => props.candidate,
  async (newCandidate) => {
    if (newCandidate?.job_applicant) {
      await fetchApplicantResume(newCandidate.job_applicant);
    } else {
      resumeData.value = null;
    }
  },
  { immediate: true }
);

async function fetchApplicantResume(applicantId) {
  if (!applicantId) return;

  loading.value = true;

  frappe.call({
    method: "mawhub.job_applicant_find",
    type: "GET",
    args: {
      job: props.jobId,
      name: applicantId
    },
    callback: function(res) {
      loading.value = false;
      if (res.message) {
        resumeData.value = res.message.resume || null;
      }
    },
    error: function(err) {
      loading.value = false;
      console.error('Failed to load applicant resume:', err);
      resumeData.value = null;
      frappe.msgprint({
        title: 'Error',
        message: 'Failed to load applicant resume',
        indicator: 'red'
      });
    }
  });
}

function getFileUrl(filePath) {
  if (!filePath) return '';
  // If the file path is already a full URL, return it
  if (filePath.startsWith('http://') || filePath.startsWith('https://')) {
    return filePath;
  }
  // Otherwise, construct the URL using Frappe's file serving endpoint
  return `${window.location.origin}${filePath}`;
}

function getFileName(filePath) {
  if (!filePath) return 'Resume';
  const parts = filePath.split('/');
  return parts[parts.length - 1] || 'Resume';
}
</script>

<style scoped>
.applicant-resume {
  padding: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.resume-container {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 400px);
  padding: 8px;
}

.resume-loading,
.resume-empty {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.resume-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.resume-empty-text {
  font-size: 14px;
  color: #9ca3af;
  text-align: center;
  margin: 0;
}

.resume-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  margin-bottom: 16px;
}

.resume-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.resume-icon {
  font-size: 32px;
  line-height: 1;
  flex-shrink: 0;
}

.resume-filename {
  font-size: 16px;
  font-weight: 600;
  color: #111827;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.resume-meta {
  font-size: 12px;
  color: #6b7280;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.resume-download-btn {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 6px;
}

.resume-viewer {
  flex: 1;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e5e7eb;
  background: #ffffff;
  position: relative;
}

.resume-pdf-embed {
  width: 100%;
  height: 100%;
  border: none;
  display: block;
}

/* Dark Mode Styles */
[data-theme="dark"] .resume-header {
  background: #2a2a2a;
  border-color: #3a3a3a;
}

[data-theme="dark"] .resume-filename {
  color: #f0f0f0;
}

[data-theme="dark"] .resume-meta {
  color: #9ca3af;
}

[data-theme="dark"] .resume-viewer {
  border-color: #3a3a3a;
  background: #2a2a2a;
}

[data-theme="dark"] .resume-empty-text {
  color: #6b7280;
}

[data-theme="dark"] .resume-loading,
[data-theme="dark"] .resume-empty {
  color: #9ca3af;
}
</style>
