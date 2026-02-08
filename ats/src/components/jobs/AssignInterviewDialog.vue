<template>
  <Dialog
    v-model="isOpen"
    :options="{
      title: `Assign Interview to ${candidateName || ''}`,
      size: 'xl',
    }"
  >
    <template #body-content>
      <div class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium mb-1">Interview Round *</label>
            <Select
              v-model="formData.interview_round"
              :options="interviewRoundOptions"
              placeholder="Select round"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Status *</label>
            <Select
              v-model="formData.status"
              :options="interviewStatusOptions"
              placeholder="Select status"
            />
          </div>
        </div>

        <div class="grid grid-cols-3 gap-4">
          <div>
            <label class="block text-sm font-medium mb-1">Scheduled Date *</label>
            <input
              v-model="formData.scheduled_on"
              type="date"
              class="form-control"
            >
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">From Time *</label>
            <input
              v-model="formData.from_time"
              type="time"
              class="form-control"
            >
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">To Time *</label>
            <input
              v-model="formData.to_time"
              type="time"
              class="form-control"
            >
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium mb-1">Expected Rating</label>
          <TextInput
            v-model.number="formData.expected_average_rating"
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
            v-model="formData.interview_summary"
            class="form-control"
            rows="3"
            placeholder="Optional notes or summary"
          />
        </div>
      </div>
    </template>
    <template #actions>
      <div class="flex justify-between w-full">
        <Button @click="close">
          Cancel
        </Button>
        <Button
          theme="gray"
          :variant="'solid'"
          :loading="isSubmitting"
          @click="submit"
        >
          Assign Interview
        </Button>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import { Dialog, Button, Select, TextInput, createResource } from 'frappe-ui';
import { useToast } from 'vue-toastification';
import { JobDetailsAPI } from '../../api/apiClient.js';

const toast = useToast();

JobDetailsAPI.init(createResource);

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  candidateId: {
    type: String,
    default: null
  },
  candidateName: {
    type: String,
    default: ''
  },
  jobId: {
    type: String,
    required: true
  },
  jobDesignation: {
    type: String,
    required: true
  },
  resumeLink: {
    type: String,
    default: ''
  }
});

const emit = defineEmits(['update:modelValue', 'success']);

const isOpen = ref(props.modelValue);
const interviewRoundOptions = ref([]);
const isLoadingRounds = ref(false);
const isSubmitting = ref(false);

const formData = ref({
  interview_round: '',
  status: 'Pending',
  scheduled_on: '',
  from_time: '',
  to_time: '',
  expected_average_rating: 0,
  interview_summary: '',
});

const interviewStatusOptions = [
  { label: 'Pending', value: 'Pending' },
  { label: 'Under Review', value: 'Under Review' },
  { label: 'Cleared', value: 'Cleared' },
  { label: 'Rejected', value: 'Rejected' },
  { label: 'Cancelled', value: 'Cancelled' },
];

onMounted(async () => {
  await fetchInterviewRounds();
});

async function fetchInterviewRounds() {
  try {
    isLoadingRounds.value = true;
    const rounds = await JobDetailsAPI.getDocList('Interview Round', {
      fields: ['name', 'round_name'],
      order_by: 'idx asc'
    });
    
    interviewRoundOptions.value = rounds.map(round => ({
      label: round.round_name || round.name,
      value: round.name
    }));
    
    if (interviewRoundOptions.value.length > 0 && !formData.value.interview_round) {
      formData.value.interview_round = interviewRoundOptions.value[0].value;
    }
  } catch (error) {
    console.error('Error fetching interview rounds:', error);
    interviewRoundOptions.value = [
      { label: 'HR Screening', value: 'HR Screening' },
      { label: 'Technical Interview', value: 'Technical Interview' },
    ];
  } finally {
    isLoadingRounds.value = false;
  }
}

watch(() => props.modelValue, (newVal) => {
  isOpen.value = newVal;
  if (newVal && interviewRoundOptions.value.length === 0) {
    fetchInterviewRounds();
  }
});

watch(isOpen, (newVal) => {
  emit('update:modelValue', newVal);
  if (!newVal) {
    resetForm();
  }
});

function resetForm() {
  formData.value = {
    interview_round: interviewRoundOptions.value.length > 0 ? interviewRoundOptions.value[0].value : '',
    status: 'Pending',
    scheduled_on: '',
    from_time: '',
    to_time: '',
    expected_average_rating: 0,
    interview_summary: '',
  };
}

async function submit() {
  if (
    !formData.value.interview_round ||
    !formData.value.status ||
    !formData.value.scheduled_on ||
    !formData.value.from_time ||
    !formData.value.to_time
  ) {
    toast.warning('Please fill in all required fields');
    return;
  }

  if (formData.value.from_time >= formData.value.to_time) {
    toast.warning('End time must be after start time');
    return;
  }

  if (!props.candidateId || !props.jobId) {
    toast.error('Candidate or job not loaded');
    return;
  }

  const payload = {
    job_applicant: props.candidateId,
    job_opening: props.jobId,
    designation: props.jobDesignation,
    interview_round: formData.value.interview_round,
    status: formData.value.status,
    scheduled_on: formData.value.scheduled_on,
    from_time: formData.value.from_time,
    to_time: formData.value.to_time,
    expected_average_rating: formData.value.expected_average_rating || 0,
    interview_summary: formData.value.interview_summary || '',
    resume_link: props.resumeLink || '',
    reminded: 0,
  };

  try {
    isSubmitting.value = true;
    await JobDetailsAPI.createOrUpdateInterview(payload);
    emit('success', {
      candidateName: props.candidateName,
      scheduledOn: formData.value.scheduled_on
    });
    close();
  } catch (error) {
    const err = error;
    toast.error(err.message || 'Failed to assign interview');
  } finally {
    isSubmitting.value = false;
  }
}

function close() {
  isOpen.value = false;
}
</script>

<style scoped>
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

.flex {
  display: flex;
}

.justify-between {
  justify-content: space-between;
}

.w-full {
  width: 100%;
}
</style>
