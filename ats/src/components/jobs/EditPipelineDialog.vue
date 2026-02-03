<template>
    <Dialog v-model="show" :options="{ title: 'Edit Pipeline', size: '3xl' }">
        <template #body-content>
            <div class="space-y-4">
                <!-- Pipeline Name -->
                <div>
                    <label class="block text-sm font-medium mb-1">Pipeline Name</label>
                    <TextInput
                        v-model="formData.name"
                        type="text"
                        placeholder="Enter pipeline name"
                    />
                </div>

                <!-- Pipeline Description -->
                <div>
                    <label class="block text-sm font-medium mb-1">Description</label>
                    <textarea
                        v-model="formData.description"
                        class="form-control"
                        rows="3"
                        placeholder="Enter pipeline description"
                    />
                </div>

                <!-- Pipeline Steps -->
                <div>
                    <div class="flex justify-between items-center mb-2">
                        <label class="block text-sm font-medium">Pipeline Steps</label>
                        <Button size="sm" @click="addStep">
                            <Plus :size="16" class="button-icon" />
                            Add Step
                        </Button>
                    </div>

                    <div class="space-y-3">
                        <div
                            v-for="(step, index) in formData.steps"
                            :key="index"
                            class="pipeline-step-item"
                        >
                            <div class="step-number">{{ index + 1 }}</div>
                            <div class="step-fields">
                                <div class="step-field">
                                    <label class="text-xs font-medium mb-1 block"
                                        >Step Name</label
                                    >
                                    <TextInput
                                        v-model="step.step_name"
                                        type="text"
                                        size="sm"
                                        placeholder="e.g., Resume Review"
                                    />
                                </div>
                                <div class="step-field">
                                    <label class="text-xs font-medium mb-1 block"
                                        >Step Type</label
                                    >
                                    <Select
                                        v-model="step.step_type"
                                        :options="stepTypeOptions"
                                        size="sm"
                                        placeholder="Select type"
                                    />
                                </div>
                            </div>
                            <Button
                                size="sm"
                                theme="gray"
                                variant="ghost"
                                @click="removeStep(index)"
                                :disabled="formData.steps.length === 1"
                            >
                                <Trash2 :size="16" />
                            </Button>
                        </div>
                    </div>
                </div>
            </div>
        </template>

        <template #actions>
            <Button variant="solid" @click="handleSubmit" :loading="isSubmitting">
                Save Changes
            </Button>
            <Button variant="outline" @click="show = false">Cancel</Button>
        </template>
    </Dialog>
</template>

<script setup>
import { ref, watch, computed } from "vue";
import { Dialog, TextInput, Select, Button } from "frappe-ui";
import { Plus, Trash2 } from "lucide-vue-next";

const props = defineProps({
    modelValue: {
        type: Boolean,
        required: true,
    },
    jobData: {
        type: Object,
        default: null,
    },
    onSubmit: {
        type: Function,
        required: true,
    },
});

const emit = defineEmits(["update:modelValue"]);

const show = computed({
    get: () => props.modelValue,
    set: (val) => emit("update:modelValue", val),
});

const stepTypeOptions = [
    { label: "Screening", value: "screening" },
    { label: "Interview", value: "interview" },
    { label: "Assessment", value: "assessment" },
    { label: "Review", value: "review" },
    { label: "Offer", value: "offer" },
    { label: "Other", value: "other" },
];

const isSubmitting = ref(false);

const formData = ref({
    name: "",
    description: "",
    steps: [],
});

// Initialize form data when dialog opens
watch(
    () => props.modelValue,
    (newVal) => {
        if (newVal && props.jobData) {
            initializeFormData();
        }
    },
    { immediate: true },
);

function initializeFormData() {
    if (!props.jobData) return;

    formData.value = {
        name: props.jobData.title || "",
        description: props.jobData.description || "",
        steps:
            props.jobData.steps && props.jobData.steps.length > 0
                ? props.jobData.steps.map((step) => ({
                      step_name: step.label || step.step_name || "",
                      step_type: step.type || step.step_type || "Other",
                      step_id: step.id || step.step_id,
                      idx: step.idx,
                  }))
                : [
                      {
                          step_name: "Initial Screening",
                          step_type: "Screening",
                      },
                  ],
    };
}

function addStep() {
    formData.value.steps.push({
        step_name: "",
        step_type: "Other",
    });
}

function removeStep(index) {
    if (formData.value.steps.length > 1) {
        formData.value.steps.splice(index, 1);
    }
}

async function handleSubmit() {
    // Validate form
    if (!formData.value.name.trim()) {
        return;
    }

    // Check if all steps have names
    const hasEmptySteps = formData.value.steps.some((step) => !step.step_name.trim());
    if (hasEmptySteps) {
        return;
    }

    try {
        isSubmitting.value = true;
        await props.onSubmit(formData.value);
        show.value = false;
    } catch (error) {
        console.error("Error submitting pipeline:", error);
    } finally {
        isSubmitting.value = false;
    }
}
</script>

<style scoped>
.space-y-4 > * + * {
    margin-top: 1rem;
}

.space-y-3 > * + * {
    margin-top: 0.75rem;
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
}

.form-control:focus {
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.pipeline-step-item {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 12px;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    background: #f9fafb;
}

.step-number {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: #111827;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
    font-weight: 700;
    flex-shrink: 0;
    margin-top: 20px;
}

.step-fields {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    flex: 1;
}

.step-field {
    display: flex;
    flex-direction: column;
}

.button-icon {
    display: inline-block;
    vertical-align: middle;
    margin-right: 6px;
}

label {
    font-size: 14px;
    color: #374151;
}

.text-xs {
    font-size: 0.75rem;
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

.block {
    display: block;
}
</style>
