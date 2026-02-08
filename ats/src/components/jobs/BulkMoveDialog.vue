<template>
  <Dialog 
    v-model="isOpen" 
    :options="{ title: 'Bulk Move Candidates', size: 'md' }"
  >
    <template #body-content>
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium mb-1">Move to Step *</label>
          <Select
            v-model="formData.target_step"
            :options="stepOptions"
            placeholder="Select target step"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Update Status (Optional)</label>
          <Select
            v-model="formData.status"
            :options="statusOptions"
            placeholder="Select status"
          />
        </div>
        <p class="text-muted text-sm">
          Moving {{ candidateCount }} candidate(s)
        </p>
      </div>
    </template>
    <template #actions>
      <Button @click="close">
        Cancel
      </Button>
      <Button
        theme="primary"
        :loading="isSubmitting"
        @click="submit"
      >
        Move Candidates
      </Button>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, watch } from 'vue';
import { Dialog, Button, Select, createResource } from 'frappe-ui';
import { useToast } from 'vue-toastification';
import { JobDetailsAPI } from '../../api/apiClient.js';

const toast = useToast();

JobDetailsAPI.init(createResource);

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  stepOptions: {
    type: Array,
    default: () => []
  },
  candidateCount: {
    type: Number,
    default: 0
  },
  candidateIds: {
    type: Array,
    required: true
  }
});

const emit = defineEmits(['update:modelValue', 'success']);

const isOpen = ref(props.modelValue);
const isSubmitting = ref(false);

const formData = ref({
  target_step: '',
  status: '',
});

const statusOptions = [
  { label: 'No Change', value: '' },
  { label: 'Open', value: 'Open' },
  { label: 'Hold', value: 'Hold' },
  { label: 'Rejected', value: 'Rejected' },
  { label: 'Hired', value: 'Hired' },
];

watch(() => props.modelValue, (newVal) => {
  isOpen.value = newVal;
});

watch(isOpen, (newVal) => {
  emit('update:modelValue', newVal);
  if (!newVal) {
    resetForm();
  }
});

function resetForm() {
  formData.value = {
    target_step: '',
    status: '',
  };
}

async function submit() {
  if (!formData.value.target_step) {
    toast.warning('Please select a target step');
    return;
  }

  const targetStepLabel =
    props.stepOptions.find((s) => s.value === formData.value.target_step)?.label || '';

  const payload = {
    names: props.candidateIds,
    pipeline_step: formData.value.target_step,
  };

  if (formData.value.status) {
    payload.status = formData.value.status;
  }

  try {
    isSubmitting.value = true;
    await JobDetailsAPI.bulkUpdateApplicants(payload);
    emit('success', {
      count: props.candidateCount,
      targetStepLabel,
      targetStepId: formData.value.target_step
    });
    close();
  } catch (error) {
    const err = error;
    toast.error(err.message || 'Failed to move candidates');
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

.text-muted {
  color: #6b7280;
}
</style>
