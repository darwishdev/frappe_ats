<template>
  <div class="applicant-communication">
    <div class="empty-state">
      <div class="empty-state-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <rect width="20" height="16" x="2" y="4" rx="2"/>
          <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
        </svg>
      </div>
      <h3 class="empty-state-title">No Communications Yet</h3>
      <p class="empty-state-description">
        Email communications with this applicant will appear here. Click "Send Email" to start a conversation.
      </p>
    <Button class="p-4 px-7 mt-3"
        theme="gray"
        :variant="'solid'"
        @click="showSendEmailDialog = true"
        :disabled="!candidate"
      >
        <Mail :size="16" class="button-icon" />
        Send Email
      </Button>
    </div>

    <!-- Send Email Dialog -->
    <SendEmailDialog
      v-model="showSendEmailDialog"
      :candidate-email="candidate?.email"
      :candidate-name="candidate?.name"
      :job-title="jobTitle"
      :on-submit="handleSendEmail"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { Button } from 'frappe-ui';
import { Mail } from 'lucide-vue-next';
import SendEmailDialog from './SendEmailDialog.vue';
import { useToast } from "vue-toastification";

const toast = useToast();

const props = defineProps({
  candidate: {
    type: Object,
    default: null,
  },
  jobTitle: {
    type: String,
    default: '',
  },
});

const showSendEmailDialog = ref(false);

async function handleSendEmail(formData) {
  try {
    // Email sending logic would go here
    toast.success(`Email sent to ${props.candidate?.name}`);
  } catch (error) {
    toast.error(error.message || 'Failed to send email');
    throw error;
  }
}
</script>

<style scoped>
.applicant-communication {
  padding: 0px 0;
}

.communication-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid #e5e7eb;
}

.communication-title {
  font-size: 18px;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

.button-icon {
  display: inline-block;
  vertical-align: middle;
  margin-right: 6px;
}

.empty-state {
  text-align: center;
  max-width: 400px;
  padding: 20px 24px;
  margin: 40px auto 0;
}

.empty-state-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 96px;
  height: 96px;
  margin: 0 auto 15px;
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
