<template>
  <Dialog
    v-model="isOpen"
    :options="{ title: 'Add Candidate', size: 'lg' }"
  >
    <template #body-content>
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium mb-1">Name *</label>
          <TextInput
            v-model="formData.name"
            type="text"
            placeholder="Enter candidate name"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Email *</label>
          <TextInput
            v-model="formData.email"
            type="email"
            placeholder="Enter email address"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Phone</label>
          <TextInput
            v-model="formData.phone"
            type="text"
            placeholder="Enter phone number"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Country</label>
          <TextInput
            v-model="formData.country"
            type="text"
            placeholder="Enter country"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Source</label>
          <Select
            v-model="formData.source"
            :options="sourceOptions"
            placeholder="Select source"
          />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium mb-1">Expected Salary (Min)</label>
            <TextInput
              v-model="formData.lower_range"
              type="number"
              placeholder="Minimum salary"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1">Expected Salary (Max)</label>
            <TextInput
              v-model="formData.upper_range"
              type="number"
              placeholder="Maximum salary"
            />
          </div>
        </div>
      </div>
    </template>
    <template #actions>
      <Button @click="close">Cancel</Button>
      <Button theme="gray" :variant="'solid'" @click="submit">Add Candidate</Button>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, watch } from 'vue';
import { Dialog, Button, Select, TextInput } from 'frappe-ui';

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  onSubmit: {
    type: Function,
    required: true
  }
});

const emit = defineEmits(['update:modelValue']);

const isOpen = ref(props.modelValue);

const formData = ref({
  name: '',
  email: '',
  phone: '',
  country: '',
  source: 'Campaign',
  lower_range: '',
  upper_range: '',
});

const sourceOptions = [
  { label: 'Campaign', value: 'Campaign' },
  { label: 'LinkedIn', value: 'LinkedIn' },
  { label: 'Referral', value: 'Referral' },
  { label: 'Direct', value: 'Direct' },
  { label: 'Other', value: 'Other' },
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
    name: '',
    email: '',
    phone: '',
    country: '',
    source: 'Campaign',
    lower_range: '',
    upper_range: '',
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

.gap-4 {
  gap: 1rem;
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
</style>
