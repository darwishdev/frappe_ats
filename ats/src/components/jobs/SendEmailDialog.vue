<template>
    <Dialog
        v-model="isOpen"
        :options="{
            title: `Send Email to  || ''}`,
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
                    <div class="flex justify-between items-center mb-1">
                        <label class="block text-sm font-medium">Message *</label>
                        <div class="flex gap-2">
                            <Button
                                size="sm"
                                class="p-4"
                                @click="togglePromptInput"
                                :disabled="isGenerating"
                            >
                                <div class="flex w-full items-center">
                                    <Settings :size="14" class="mr-1" />
                                    Custom Instructions
                                </div>
                            </Button>
                            <Button
                                size="sm"
                                class="p-4"
                                theme="gray"
                                :variant="'solid'"
                                @click="generateEmailContent"
                                :loading="isGenerating"
                            >
                                <div class="flex w-full items-center">
                                    <Sparkles :size="14" class="mr-1" v-if="!isGenerating" />
                                    {{ isGenerating ? "Generating..." : "Generate with AI" }}
                                </div>
                            </Button>
                        </div>
                    </div>

                    <!-- Custom Prompt Input (collapsible) -->
                    <div v-if="showPromptInput" class="prompt-input-container">
                        <textarea
                            v-model="customPrompt"
                            class="form-control prompt-textarea"
                            rows="3"
                            placeholder="Enter custom instructions for the AI (e.g., 'Keep it formal and brief', 'Mention the interview date'...)"
                        ></textarea>
                    </div>

                    <textarea
                        v-model="formData.message"
                        class="form-control mt-1"
                        rows="8"
                        placeholder="Write your email message here or generate with AI..."
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
                    <label for="send-copy" class="text-sm cursor-pointer"> Send me a copy </label>
                </div>
            </div>
        </template>
        <template #actions>
            <div class="flex justify-between w-full gap-2">
                <Button @click="close">Cancel</Button>
                <div class="flex items-center gap-3">
                    <Button
                        @click="saveAsTemplate"
                        :disabled="!formData.message || isSavingTemplate"
                        :loading="isSavingTemplate"
                    >
                        <div class="flex items-center gap-1">
                            <Save :size="15" class="mr-1" v-if="!isSavingTemplate" />
                            {{ isSavingTemplate ? "Saving..." : "Save as Template" }}
                        </div>
                    </Button>
                    <Button theme="gray" :variant="'solid'" @click="submit">Send Email</Button>
                </div>
            </div>
        </template>
    </Dialog>

    <!-- Template Name Dialog -->
    <Dialog
        v-model="showTemplateNameDialog"
        :options="{
            title: 'Save Email Template',
            size: 'sm',
        }"
    >
        <template #body-content>
            <div class="space-y-4">
                <div>
                    <label class="block text-sm font-medium mb-2">Template Name *</label>
                    <TextInput
                        v-model="templateName"
                        type="text"
                        placeholder="e.g., Interview Confirmation, Rejection, Offer"
                        @keyup.enter="confirmSaveTemplate"
                    />
                </div>
                <div>
                    <label class="block text-sm font-medium mb-2">Description (Optional)</label>
                    <textarea
                        v-model="templateDescription"
                        class="form-control"
                        rows="3"
                        placeholder="Add notes about when to use this template..."
                    ></textarea>
                </div>
            </div>
        </template>
        <template #actions>
            <Button @click="closeTemplateDialog">Cancel</Button>
            <Button
                theme="gray"
                :variant="'solid'"
                @click="confirmSaveTemplate"
                :disabled="!templateName || !templateName.trim()"
            >
                Save Template
            </Button>
        </template>
    </Dialog>
</template>

<script setup>
import { ref, watch } from "vue";
import { Dialog, Button, TextInput } from "frappe-ui";
import { Sparkles, Settings, Save } from "lucide-vue-next";
import { useToast } from "vue-toastification";
import { JobDetailsAPI } from "../../api/apiClient.js";

const toast = useToast();

const props = defineProps({
    modelValue: {
        type: Boolean,
        default: false,
    },
    candidate: {
        default: "",
    },
    step: {
        type: String,
        default: "",
    },
    job: {
        default: "",
    },
    onSubmit: {
        type: Function,
        required: true,
    },
});

const emit = defineEmits(["update:modelValue"]);

const isOpen = ref(props.modelValue);

const formData = ref({
    to: "",
    subject: "",
    message: "",
    cc: "",
    bcc: "",
    send_me_a_copy: false,
});

const isGenerating = ref(false);
const showPromptInput = ref(false);
const customPrompt = ref("");

const isSavingTemplate = ref(false);
const showTemplateNameDialog = ref(false);
const templateName = ref("");
const templateDescription = ref("");

watch(
    () => props.modelValue,
    (newVal) => {
        isOpen.value = newVal;
        if (newVal) {
            // Pre-fill form data when dialog opens
            formData.value.to = props.candidateEmail;
            if (props.jobTitle) {
                formData.value.subject = `Regarding your application for ${props.jobTitle}`;
            }
        }
    },
);

watch(isOpen, (newVal) => {
    emit("update:modelValue", newVal);
    if (!newVal) {
        resetForm();
    }
});

function resetForm() {
    formData.value = {
        to: "",
        subject: "",
        message: "",
        cc: "",
        bcc: "",
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

function togglePromptInput() {
    showPromptInput.value = !showPromptInput.value;
}

async function generateEmailContent() {
    if (!props.candidate) {
        toast.warning("Candidate information is required to generate email");
        return;
    }

    isGenerating.value = true;

    try {
        const payload = {
            applicant: props.candidate,
            pipeline_step: props.step,
            job: props.job,
        };

        const response = await JobDetailsAPI.generateEmail(payload);

        if (response && response.message) {
            formData.value.message = response.message
                .replace(/<br\s*\/?>/gi, "\n")
                .replace(/<\/p>/gi, "\n\n")
                .replace(/<[^>]*>/g, "");
            toast.success("Email content generated successfully!");
        } else {
            throw new Error("Invalid response from AI");
        }
    } catch (error) {
        console.error("Failed to generate email:", error);
        toast.error(`Failed to generate email: ${error.message || "Unknown error"}`);
    } finally {
        isGenerating.value = false;
    }
}

function saveAsTemplate() {
    if (!formData.value.message || !formData.value.message.trim()) {
        toast.warning("Please write a message to save as template");
        return;
    }

    templateName.value = "";
    templateDescription.value = "";
    showTemplateNameDialog.value = true;
}

function closeTemplateDialog() {
    showTemplateNameDialog.value = false;
}

async function confirmSaveTemplate() {
    if (!templateName.value || !templateName.value.trim()) {
        toast.warning("Please enter a template name");
        return;
    }

    isSavingTemplate.value = true;

    try {
        const payload = {
            template_name: templateName.value,
            description: templateDescription.value || "",
            subject: formData.value.subject,
            message: formData.value.message,
        };

        const response = await JobDetailsAPI.saveEmailTemplate(payload);

        if (response) {
            toast.success(`Template "${templateName.value}" saved successfully!`);
            closeTemplateDialog();
        } else {
            throw new Error("Invalid response from server");
        }
    } catch (error) {
        console.error("Failed to save template:", error);
        toast.error(`Failed to save template: ${error.message || "Unknown error"}`);
    } finally {
        isSavingTemplate.value = false;
    }
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

.mb-2 {
    margin-bottom: 0.5rem;
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

.prompt-input-container {
    margin-bottom: 8px;
    animation: slideDown 0.2s ease-out;
}

@keyframes slideDown {
    from {
        opacity: 0;
        transform: translateY(-10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.prompt-textarea {
    background-color: #f8fafc;
    border-color: #cbd5e1;
    font-size: 13px;
}

.prompt-textarea::placeholder {
    color: #94a3b8;
    font-size: 12px;
}

.mr-1 {
    margin-right: 0.25rem;
}

.mt-1 {
    margin-top: 0.25rem;
}
</style>
