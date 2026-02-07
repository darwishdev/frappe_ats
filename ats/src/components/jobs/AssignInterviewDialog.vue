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
import { Dialog, Button, Select, TextInput } from 'frappe-ui';
import { JobDetailsAPI } from '../../api/apiClient.js';

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
  onSubmit: {
    type: Function,
    required: true
  }
});

const emit = defineEmits(['update:modelValue']);

const isOpen = ref(props.modelValue);
const interviewRoundOptions = ref([]);
const isLoadingRounds = ref(false);

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

// Fetch interview rounds on component mount
onMounted(async () => {
  await fetchInterviewRounds();
});

// Fetch interview rounds dynamically
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
    
    // Set default value to first option if available
    if (interviewRoundOptions.value.length > 0 && !formData.value.interview_round) {
      formData.value.interview_round = interviewRoundOptions.value[0].value;
    }
  } catch (error) {
    console.error('Error fetching interview rounds:', error);
    // Fallback to basic options if fetch fails
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
    // Fetch rounds if dialog opens and rounds not yet loaded
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
  await props.onSubmit(formData.value);
  close();
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
