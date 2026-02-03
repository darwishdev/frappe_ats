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
                                        >Step Code</label
                                    >
                                    <TextInput
                                        v-model="step.step_code"
                                        type="text"
                                        size="sm"
                                        placeholder="e.g., SC"
                                    />
                                </div>
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
            <div class="flex w-full justify-between items-center">
                <Button variant="outline" @click="show = false">Cancel</Button>
                <Button variant="solid" @click="handleSubmit" :loading="isSubmitting">
                    Save Changes
                </Button>
            </div>
        </template>
    </Dialog>
</template>

<script setup>
import { ref, watch, computed } from "vue";
import { Dialog, TextInput, Select, Button } from "frappe-ui";
import { Plus, Trash2 } from "lucide-vue-next";
import { JobDetailsAPI } from "../../api/apiClient.js";

const props = defineProps({
    modelValue: {
        type: Boolean,
        required: true,
    },
    jobData: {
        type: Object,
        default: null,
    },
    pipelineData: {
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

    // Use pipelineData if available, otherwise use jobData
    const pipeline = props.pipelineData || {};
    
    formData.value = {
        name: pipeline.name || props.jobData.pipeline_name || props.jobData.title || "",
        description: pipeline.description || "",
        steps:
            pipeline.steps && pipeline.steps.length > 0
                ? pipeline.steps.map((step) => ({
                      name: step.name || step.step_code || "",
                      step_name: step.step_name || "",
                      step_type: step.step_type || "Other",
                      step_code: step.step_code || step.name || "",
                      idx: step.idx,
                      doctype: "Pipeline Step",
                  }))
                : props.jobData.steps && props.jobData.steps.length > 0
                ? props.jobData.steps.map((step, index) => ({
                      name: step.id || step.step_id || "",
                      step_name: step.label || step.step_name || "",
                      step_type: step.type || step.step_type || "Other",
                      step_code: step.id || step.step_id || "",
                      idx: step.idx || index + 1,
                      doctype: "Pipeline Step",
                  }))
                : [
                      {
                          name: "SC",
                          step_name: "Initial Screening",
                          step_type: "Screening",
                          step_code: "SC",
                          idx: 1,
                          doctype: "Pipeline Step",
                      },
                  ],
    };
}

function addStep() {
    const newIdx = formData.value.steps.length + 1;
    formData.value.steps.push({
        name: `new-pipeline-step-${Date.now()}`,
        step_name: "",
        step_type: "Other",
        step_code: "",
        idx: newIdx,
        doctype: "Pipeline Step",
        docstatus: 0,
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
    console.log(formData.value);
    

    // Check if all steps have names and codes
    const hasEmptySteps = formData.value.steps.some(
        (step) => !step.step_name.trim() || !step.step_code
    );
    if (hasEmptySteps) {
        return;
    }

    try {
        isSubmitting.value = true;
        
        // Fetch the latest pipeline document to get current timestamps
        let latestPipeline = null;
        try {
            latestPipeline = await JobDetailsAPI.getPipeline(formData.value.name);
        } catch (error) {
            console.log("Pipeline not found, creating new one");
        }
        
        // Construct the Frappe document payload
        const pipeline = latestPipeline || props.pipelineData || {};
        const now = new Date().toISOString().replace('T', ' ').split('.')[0];
        
        const pipelineDoc = {
            name: formData.value.name,
            doctype: "Job Pipeline",
            description: formData.value.description || "",
            is_primary: pipeline.is_primary || 0,
            docstatus: 0,
            idx: 0,
            owner: pipeline.owner || "Administrator",
            creation: pipeline.creation || now,
            modified: pipeline.modified || now, // Use actual modified timestamp from DB
            modified_by: pipeline.modified_by || "Administrator",
            steps: formData.value.steps.map((step, index) => {
                // Find existing step to preserve its timestamps
                const existingStep = latestPipeline?.steps?.find(s => 
                    s.name === step.name || s.step_code === step.step_code
                );
                
                return {
                    name: step.name || step.step_code,
                    doctype: "Pipeline Step",
                    step_code: step.step_code || step.name,
                    step_name: step.step_name,
                    step_type: step.step_type.toLowerCase(),
                    idx: index + 1,
                    docstatus: 0,
                    parent: formData.value.name,
                    parentfield: "steps",
                    parenttype: "Job Pipeline",
                    owner: existingStep?.owner || "Administrator",
                    creation: existingStep?.creation || now,
                    modified: existingStep?.modified || now,
                    modified_by: existingStep?.modified_by || "Administrator",
                };
            }),
        };

        // Call the API through the onSubmit prop
        await props.onSubmit(pipelineDoc);
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
    grid-template-columns: 0.8fr 1.2fr 1fr;
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
