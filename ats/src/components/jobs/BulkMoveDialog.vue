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
        <p class="text-muted text-sm">Moving {{ candidateCount }} candidate(s)</p>
      </div>
    </template>
    <template #actions>
      <Button @click="close">Cancel</Button>
      <Button theme="primary" @click="submit">Move Candidates</Button>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, watch } from 'vue';
import { Dialog, Button, Select } from 'frappe-ui';

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
  onSubmit: {
    type: Function,
    required: true
  }
});

const emit = defineEmits(['update:modelValue']);

const isOpen = ref(props.modelValue);

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
