<template>
  <div class="applicant-timeline">
    <div class="timeline-container">
      <div v-if="loading" class="timeline-loading">
        <div style="text-align: center; padding: 40px; color: #888;">
          Loading timeline...
        </div>
      </div>
      <div v-else-if="timelineEvents.length > 0" class="timeline-list">
        <div
          v-for="event in timelineEvents"
          :key="event.name"
          class="timeline-item"
        >
          <div class="timeline-marker"></div>
          <div class="timeline-content">
            <div class="timeline-header">
              <h4 class="timeline-title">{{ event.action }}</h4>
              <span class="timeline-date">{{ formatDate(event.creation) }}</span>
            </div>
            <p v-if="event.comment" class="timeline-description">
              {{ event.comment }}
            </p>
            <span class="timeline-user">by {{ event.owner }}</span>
          </div>
        </div>
      </div>
      <div v-else class="timeline-empty">
        <p>No timeline events yet</p>
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
  }
});

const loading = ref(false);
const timelineEvents = ref([]);

watch(
  () => props.candidate,
  async (newCandidate) => {
    if (newCandidate?.job_applicant) {
      await fetchTimeline(newCandidate.job_applicant);
    } else {
      timelineEvents.value = [];
    }
  },
  { immediate: true }
);

async function fetchTimeline(applicantId) {
  if (!applicantId) return;
  
  loading.value = true;
  
  frappe.call({
    method: 'frappe.desk.reportview.get',
    args: {
      doctype: 'Comment',
      fields: [
        "`tabComment`.`name`",
        "`tabComment`.`owner`",
        "`tabComment`.`creation`",
        "`tabComment`.`comment_by`",
        "`tabComment`.`content`",
        "`tabComment`.`comment_type`"
      ],
      filters: [["Comment", "reference_name", "=", applicantId]],
      order_by: "`tabComment`.`creation` desc"
    },
    callback: function(res) {
      loading.value = false;
      if (res.message && res.message.values) {
        // Map the array values to objects based on keys
        const keys = res.message.keys || [];
        timelineEvents.value = res.message.values.map(valueArray => {
          const eventObj = {};
          keys.forEach((key, index) => {
            eventObj[key] = valueArray[index];
          });
          // Add action field for display
          eventObj.action = eventObj.comment_type || 'Activity';
          eventObj.comment = eventObj.content;
          return eventObj;
        });
      } else {
        timelineEvents.value = [];
      }
    },
    error: function(err) {
      loading.value = false;
      timelineEvents.value = [];
      console.error('Failed to load timeline:', err);
    }
  });
}

function formatDate(dateStr) {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}
</script>

<style scoped>
.applicant-timeline {
  padding: 8px;
}

.timeline-container {
  max-height: calc(100vh - 400px);
  overflow-y: auto;
}

.timeline-loading,
.timeline-empty {
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #888;
}

.timeline-list {
  position: relative;
  padding-left: 30px;
}

.timeline-list::before {
  content: '';
  position: absolute;
  left: 8px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: #e5e7eb;
}

.timeline-item {
  position: relative;
  margin-bottom: 24px;
}

.timeline-marker {
  position: absolute;
  left: -26px;
  top: 4px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #667eea;
  border: 3px solid white;
  box-shadow: 0 0 0 2px #667eea;
}

.timeline-content {
  background: #f9fafb;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #e5e7eb;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.timeline-title {
  font-size: 16px;
  font-weight: 600;
  color: #111827;
  margin: 0;
}

.timeline-date {
  font-size: 12px;
  color: #9ca3af;
}

.timeline-description {
  font-size: 14px;
  color: #4b5563;
  margin: 8px 0;
}

.timeline-user {
  font-size: 12px;
  color: #6b7280;
  font-style: italic;
}

/* Dark Mode Styles */
[data-theme="dark"] .timeline-loading,
[data-theme="dark"] .timeline-empty {
  color: #9ca3af;
}

[data-theme="dark"] .timeline-list::before {
  background: #3a3a3a;
}

[data-theme="dark"] .timeline-marker {
  background: #667eea;
  border-color: #2a2a2a;
  box-shadow: 0 0 0 2px #667eea;
}

[data-theme="dark"] .timeline-content {
  background: #2a2a2a;
  border-color: #3a3a3a;
}

[data-theme="dark"] .timeline-title {
  color: #f0f0f0;
}

[data-theme="dark"] .timeline-date {
  color: #6b7280;
}

[data-theme="dark"] .timeline-description {
  color: #d1d5db;
}

[data-theme="dark"] .timeline-user {
  color: #9ca3af;
}
</style>
