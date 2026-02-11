<template>
  <div class="applicant-communication">
    <div class="communication-container">
      <div v-if="loading" class="communication-loading">
        <div style="text-align: center; padding: 40px; color: #888;">
          Loading communications...
        </div>
      </div>
      <div v-else-if="communications.length > 0" class="communication-list">
        <div
          v-for="comm in communications"
          :key="comm.name"
          class="communication-item"
        >
          <div class="communication-header">
            <div class="communication-from">
              <strong>From:</strong> {{ comm.sender }}
            </div>
            <div class="communication-date">
              {{ formatDate(comm.creation) }}
            </div>
          </div>
          <div v-if="comm.subject" class="communication-subject">
            {{ comm.subject }}
          </div>
          <div class="communication-content" v-html="comm.content"></div>
        </div>
      </div>
      <div v-else class="communication-empty">
        <p>No communications yet</p>
        <button class="btn btn-sm btn-default" @click="composeEmail">
          <span class="fa fa-envelope"></span> Send Email
        </button>
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
const communications = ref([]);

watch(
  () => props.candidate,
  async (newCandidate) => {
    if (newCandidate?.job_applicant) {
      await fetchCommunications(newCandidate.job_applicant);
    } else {
      communications.value = [];
    }
  },
  { immediate: true }
);

async function fetchCommunications(applicantId) {
  if (!applicantId) return;
  
  loading.value = true;
  
  frappe.call({
    method: 'frappe.desk.reportview.get',
    args: {
      doctype: 'Communication',
      fields: [
        "`tabCommunication`.`name`",
        "`tabCommunication`.`owner`",
        "`tabCommunication`.`creation`",
        "`tabCommunication`.`sender`",
        "`tabCommunication`.`subject`",
        "`tabCommunication`.`content`",
        "`tabCommunication`.`communication_type`",
        "`tabCommunication`.`reference_doctype`",
        "`tabCommunication`.`reference_name`"
      ],
      filters: [
        ["Communication", "reference_name", "=", applicantId],
        ["Communication", "communication_type", "in", ["Communication", "Email"]]
      ]
    },
    callback: function(res) {
      loading.value = false;
      if (res.message && res.message.values) {
        // Map the array values to objects based on keys
        const keys = res.message.keys || [];
        communications.value = res.message.values.map(valueArray => {
          const commObj = {};
          keys.forEach((key, index) => {
            commObj[key] = valueArray[index];
          });
          return commObj;
        });
      } else {
        communications.value = [];
      }
    },
    error: function(err) {
      loading.value = false;
      communications.value = [];
      console.error('Failed to load communications:', err);
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

function composeEmail() {
  if (!props.candidate) return;
  
  const dialog = new frappe.ui.Dialog({
    title: `Send Email to ${props.candidate.job_applicant}`,
    fields: [
      {
        fieldtype: 'Data',
        fieldname: 'recipient',
        label: 'To',
        default: props.candidate.applicant_email,
        read_only: 1
      },
      {
        fieldtype: 'Data',
        fieldname: 'subject',
        label: 'Subject',
        reqd: 1
      },
      {
        fieldtype: 'Text Editor',
        fieldname: 'message',
        label: 'Message',
        reqd: 1
      }
    ],
    primary_action_label: 'Send',
    primary_action: (values) => {
      frappe.call({
        method: 'frappe.core.doctype.communication.email.make',
        args: {
          recipients: values.recipient,
          subject: values.subject,
          content: values.message,
          doctype: 'Job Applicant',
          name: props.candidate.job_applicant,
          send_email: 1
        },
        callback: function() {
          frappe.show_alert({
            message: 'Email sent successfully',
            indicator: 'green'
          });
          dialog.hide();
          fetchCommunications(props.candidate.job_applicant);
        }
      });
    }
  });
  
  dialog.show();
}
</script>

<style scoped>
.applicant-communication {
  padding: 8px;
}

.communication-container {
  max-height: calc(100vh - 400px);
  overflow-y: auto;
}

.communication-loading,
.communication-empty {
  min-height: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  color: #888;
}

.communication-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.communication-item {
  background: #f9fafb;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #e5e7eb;
}

.communication-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e5e7eb;
}

.communication-from {
  font-size: 14px;
  color: #111827;
}

.communication-date {
  font-size: 12px;
  color: #9ca3af;
}

.communication-subject {
  font-size: 16px;
  font-weight: 600;
  color: #111827;
  margin-bottom: 12px;
}

.communication-content {
  font-size: 14px;
  line-height: 1.6;
  color: #4b5563;
}

.communication-content :deep(p) {
  margin: 0 0 8px 0;
}

/* Dark Mode Styles */
[data-theme="dark"] .communication-loading,
[data-theme="dark"] .communication-empty {
  color: #9ca3af;
}

[data-theme="dark"] .communication-item {
  background: #2a2a2a;
  border-color: #3a3a3a;
}

[data-theme="dark"] .communication-header {
  border-bottom-color: #3a3a3a;
}

[data-theme="dark"] .communication-from {
  color: #f0f0f0;
}

[data-theme="dark"] .communication-date {
  color: #6b7280;
}

[data-theme="dark"] .communication-subject {
  color: #f0f0f0;
}

[data-theme="dark"] .communication-content {
  color: #d1d5db;
}
</style>
