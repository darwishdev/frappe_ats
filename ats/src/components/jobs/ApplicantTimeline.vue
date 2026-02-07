<template>
  <div class="applicant-timeline">
    <div
      v-if="loading"
      class="loading-state"
    >
      <div class="loading-spinner" />
      <p>Loading interviews...</p>
    </div>
    
    <div
      v-else-if="interviews && interviews.length > 0"
      class="timeline-content"
    >
      <div class="timeline-header">
        <h3 class="timeline-title">
          Interview History
        </h3>
        <span class="interview-count">{{ interviews.length }} interview{{ interviews.length > 1 ? 's' : '' }}</span>
      </div>
      
      <div class="timeline-list">
        <div
          v-for="interview in sortedInterviews"
          :key="interview.name"
          class="timeline-item"
        >
          <div class="timeline-marker">
            <div :class="['timeline-dot', getStatusClass(interview.status)]" />
            <div class="timeline-line" />
          </div>
          
          <div class="timeline-card">
            <div class="interview-header">
              <div>
                <h4 class="interview-round">
                  {{ interview.interview_round }}
                </h4>
                <div class="interview-meta">
                  <span class="interview-id">{{ interview.name }}</span>
                  <span class="interview-designation">{{ interview.designation }}</span>
                </div>
              </div>
              <div :class="['interview-status', getStatusClass(interview.status)]">
                {{ interview.status }}
              </div>
            </div>
            
            <div class="interview-details">
              <div class="interview-detail-row">
                <div class="interview-detail-item">
                  <Calendar
                    :size="20"
                    class="detail-icon"
                  />
                  <div>
                    <div class="detail-label">
                      Scheduled Date
                    </div>
                    <div class="detail-value">
                      {{ formatDate(interview.scheduled_on) }}
                    </div>
                  </div>
                </div>
                
                <div class="interview-detail-item">
                  <Clock
                    :size="20"
                    class="detail-icon"
                  />
                  <div>
                    <div class="detail-label">
                      Time
                    </div>
                    <div class="detail-value">
                      {{ formatTime(interview.from_time) }} - {{ formatTime(interview.to_time) }}
                    </div>
                  </div>
                </div>
                
                <div
                  v-if="interview.expected_average_rating"
                  class="interview-detail-item"
                >
                  <Star
                    :size="20"
                    class="detail-icon"
                  />
                  <div>
                    <div class="detail-label">
                      Expected Rating
                    </div>
                    <div class="detail-value">
                      {{ interview.expected_average_rating }}/5
                    </div>
                  </div>
                </div>
                
                <div
                  v-if="interview.average_rating"
                  class="interview-detail-item"
                >
                  <Sparkles
                    :size="20"
                    class="detail-icon"
                  />
                  <div>
                    <div class="detail-label">
                      Actual Rating
                    </div>
                    <div class="detail-value">
                      {{ interview.average_rating }}/5
                    </div>
                  </div>
                </div>
              </div>
              
              <div
                v-if="interview.interview_summary"
                class="interview-summary"
              >
                <div class="summary-label">
                  Summary
                </div>
                <p class="summary-text">
                  {{ interview.interview_summary }}
                </p>
              </div>
              
              <div class="interview-footer">
                <span class="interview-timestamp">Created: {{ formatDateTime(interview.creation) }}</span>
                <span
                  v-if="interview.modified !== interview.creation"
                  class="interview-timestamp"
                >Modified: {{ formatDateTime(interview.modified) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div
      v-else
      class="empty-state"
    >
      <div class="empty-state-icon">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="64"
          height="64"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M8 2v4m8-4v4M3 10h18M5 4h14a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z" />
        </svg>
      </div>
      <h3 class="empty-state-title">
        No Interviews Yet
      </h3>
      <p class="empty-state-description">
        Interviews will appear here once they are scheduled for this applicant.
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { Calendar, Clock, Star, Sparkles } from 'lucide-vue-next';
import { JobDetailsAPI } from '../../api/apiClient.js';

const props = defineProps({
  candidate: {
    type: Object,
    default: null,
  },
});

const interviews = ref([]);
const loading = ref(false);

const sortedInterviews = computed(() => {
  return [...interviews.value].sort((a, b) => {
    return new Date(b.creation) - new Date(a.creation);
  });
});

function getStatusClass(status) {
  const statusMap = {
    'Pending': 'status-pending',
    'Under Review': 'status-review',
    'Cleared': 'status-cleared',
    'Rejected': 'status-rejected',
    'Cancelled': 'status-cancelled'
  };
  return statusMap[status] || 'status-default';
}

function formatDate(dateStr) {
  if (!dateStr) return 'N/A';
  try {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric' 
    });
  } catch {
    return dateStr;
  }
}

function formatTime(timeStr) {
  if (!timeStr) return 'N/A';
  try {
    // Handle time string like "1:53:00"
    const [hours, minutes] = timeStr.split(':');
    const hour = parseInt(hours);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour % 12 || 12;
    return `${displayHour}:${minutes} ${ampm}`;
  } catch {
    return timeStr;
  }
}

function formatDateTime(dateTimeStr) {
  if (!dateTimeStr) return 'N/A';
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

async function loadInterviews() {
  if (!props.candidate?.id) return;
  
  try {
    loading.value = true;
    const profile = await JobDetailsAPI.jobApplicantFind(props.candidate.id);
    interviews.value = profile.interviews || [];
  } catch (error) {
    console.error('Error loading interviews:', error);
    interviews.value = [];
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadInterviews();
});

watch(() => props.candidate?.id, () => {
  loadInterviews();
});
</script>

<style scoped>
.applicant-timeline {
  padding: 16px 0;
  min-height: 300px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  color: #6b7280;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e5e7eb;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.timeline-content {
  padding: 0 16px;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 12px;
  border-bottom: 2px solid #e5e7eb;
}

.timeline-title {
  font-size: 18px;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

.interview-count {
  font-size: 14px;
  font-weight: 600;
  color: #6b7280;
  background: #f3f4f6;
  padding: 4px 12px;
  border-radius: 12px;
}

.timeline-list {
  position: relative;
}

.timeline-item {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}

.timeline-item:last-child .timeline-line {
  display: none;
}

.timeline-marker {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 4px;
}

.timeline-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid #fff;
  box-shadow: 0 0 0 2px #e5e7eb;
  flex-shrink: 0;
}

.timeline-dot.status-pending {
  background: #fbbf24;
  box-shadow: 0 0 0 2px #fef3c7;
}

.timeline-dot.status-review {
  background: #3b82f6;
  box-shadow: 0 0 0 2px #dbeafe;
}

.timeline-dot.status-cleared {
  background: #10b981;
  box-shadow: 0 0 0 2px #d1fae5;
}

.timeline-dot.status-rejected {
  background: #ef4444;
  box-shadow: 0 0 0 2px #fee2e2;
}

.timeline-dot.status-cancelled {
  background: #6b7280;
  box-shadow: 0 0 0 2px #e5e7eb;
}

.timeline-line {
  width: 2px;
  flex: 1;
  background: #e5e7eb;
  margin-top: 4px;
}

.timeline-card {
  flex: 1;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  transition: box-shadow 0.2s;
}

.timeline-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.interview-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f3f4f6;
}

.interview-round {
  font-size: 16px;
  font-weight: 700;
  color: #111827;
  margin: 0 0 6px 0;
}

.interview-meta {
  display: flex;
  gap: 12px;
  font-size: 13px;
  color: #6b7280;
}

.interview-id {
  font-family: 'Courier New', monospace;
  background: #f3f4f6;
  padding: 2px 6px;
  border-radius: 4px;
}

.interview-designation {
  font-style: italic;
}

.interview-status {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.interview-status.status-pending {
  background: #fef3c7;
  color: #92400e;
}

.interview-status.status-review {
  background: #dbeafe;
  color: #1e40af;
}

.interview-status.status-cleared {
  background: #d1fae5;
  color: #065f46;
}

.interview-status.status-rejected {
  background: #fee2e2;
  color: #991b1b;
}

.interview-status.status-cancelled {
  background: #f3f4f6;
  color: #374151;
}

.interview-details {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.interview-detail-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.interview-detail-item {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}

.detail-icon {
  color: #6b7280;
  flex-shrink: 0;
}

.detail-label {
  font-size: 12px;
  color: #6b7280;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 2px;
}

.detail-value {
  font-size: 14px;
  color: #111827;
  font-weight: 600;
}

.interview-summary {
  background: #f9fafb;
  padding: 12px;
  border-radius: 6px;
  margin-top: 8px;
}

.summary-label {
  font-size: 12px;
  color: #6b7280;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 6px;
}

.summary-text {
  font-size: 14px;
  color: #374151;
  line-height: 1.6;
  margin: 0;
}

.interview-footer {
  display: flex;
  gap: 16px;
  padding-top: 12px;
  margin-top: 12px;
  border-top: 1px solid #f3f4f6;
}

.interview-timestamp {
  font-size: 12px;
  color: #9ca3af;
}

.empty-state {
  text-align: center;
  max-width: 400px;
  padding: 48px 24px;
  margin: 0 auto;
}

.empty-state-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 96px;
  height: 96px;
  margin: 0 auto 24px;
  background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
  border-radius: 50%;
  color: #9ca3af;
}

.empty-state-title {
  font-size: 20px;
  font-weight: 700;
  color: #111827;
  margin: 0 0 12px 0;
}

.empty-state-description {
  font-size: 15px;
  line-height: 1.6;
  color: #6b7280;
  margin: 0;
}
</style>
