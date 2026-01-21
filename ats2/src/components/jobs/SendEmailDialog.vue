<template>
  <Dialog
    v-model="isOpen"
    :options="{
      title: `Send Email to ${candidateName || ''}`,
      size: 'xl',
    }"
  >
    <template #body-content>
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium mb-1">To *</label>
          <TextInput
            v-model="formData.to"
            type="email"
            placeholder="Recipient email"
            :disabled="true"
          />
        </div>

        <div>
          <label class="block text-sm font-medium mb-1">Subject *</label>
          <TextInput
            v-model="formData.subject"
            type="text"
            placeholder="Email subject"
          />
        </div>

        <div>
          <label class="block text-sm font-medium mb-1">Message *</label>
          <textarea
            v-model="formData.message"
            class="form-control"
            rows="8"
            placeholder="Write your email message here..."
          ></textarea>
        </div>

        <div>
          <label class="block text-sm font-medium mb-1">CC</label>
          <TextInput
            v-model="formData.cc"
            type="text"
            placeholder="CC emails (comma separated)"
          />
        </div>

        <div>
          <label class="block text-sm font-medium mb-1">BCC</label>
          <TextInput
            v-model="formData.bcc"
            type="text"
            placeholder="BCC emails (comma separated)"
          />
        </div>

        <div class="flex items-center gap-2">
          <input
            id="send-copy"
            v-model="formData.send_me_a_copy"
            type="checkbox"
            class="checkbox"
          />
          <label for="send-copy" class="text-sm cursor-pointer">
            Send me a copy
          </label>
        </div>
      </div>
    </template>
    <template #actions>
      <div class="flex justify-between w-full">
        <Button @click="close">Cancel</Button>
        <Button theme="gray" :variant="'solid'" @click="submit">Send Email</Button>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, watch } from 'vue';
import { Dialog, Button, TextInput } from 'frappe-ui';

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  candidateEmail: {
    type: String,
    default: ''
  },
  candidateName: {
    type: String,
    default: ''
  },
  jobTitle: {
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

const formData = ref({
  to: '',
  subject: '',
  message: '',
  cc: '',
  bcc: '',
  send_me_a_copy: false,
});

watch(() => props.modelValue, (newVal) => {
  isOpen.value = newVal;
  if (newVal) {
    // Pre-fill form data when dialog opens
    formData.value.to = props.candidateEmail;
    if (props.jobTitle) {
      formData.value.subject = `Regarding your application for ${props.jobTitle}`;
    }
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
    to: '',
    subject: '',
    message: '',
    cc: '',
    bcc: '',
    send_me_a_copy: false,
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

.form-control {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
  font-family: inherit;
  resize: vertical;
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

.items-center {
  align-items: center;
}

.gap-2 {
  gap: 0.5rem;
}

.justify-between {
  justify-content: space-between;
}

.w-full {
  width: 100%;
}

.checkbox {
  width: 16px;
  height: 16px;
  cursor: pointer;
  border-radius: 4px;
}

.cursor-pointer {
  cursor: pointer;
}
</style>
