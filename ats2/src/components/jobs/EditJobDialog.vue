<template>
    <Dialog v-model="show" :options="{ title: mode === 'job' ? 'Edit Job' : 'Edit Job Parsed Document', size: '3xl' }">
        <template #body-content>
            <div v-if="isLoading" class="text-center py-8">
                <div class="text-gray-500">Loading job details...</div>
            </div>

            <div v-else-if="loadError" class="text-center py-8">
                <div class="text-red-500">Error loading job: {{ loadError }}</div>
            </div>

            <div v-else-if="mode === 'job'" class="space-y-6 overflow-y-auto h-[70vh]">
                <!-- Job Title -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                        Job Title <span class="text-red-500">*</span>
                    </label>
                    <TextInput
                        v-model="formData.job_title"
                        type="text"
                        placeholder="Enter job title"
                        size="md"
                    />
                </div>

                <div class="grid grid-cols-2 gap-4">
                    <!-- Department -->
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">
                            Department
                        </label>
                        <TextInput
                            v-model="formData.department"
                            type="text"
                            placeholder="Enter department"
                            size="md"
                        />
                    </div>

                    <!-- Vacancies -->
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">
                            Vacancies <span class="text-red-500">*</span>
                        </label>
                        <TextInput
                            v-model.number="formData.vacancies"
                            type="number"
                            placeholder="Number of vacancies"
                            size="md"
                        />
                    </div>
                </div>

                <div class="grid grid-cols-2 gap-4">
                    <!-- Employment Type -->
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">
                            Employment Type
                        </label>
                        <Select
                            v-model="formData.employment_type"
                            :options="employmentTypeOptions"
                            placeholder="Select employment type"
                        />
                    </div>

                    <!-- Status -->
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">
                            Status
                        </label>
                        <Select
                            v-model="formData.status"
                            :options="statusOptions"
                            placeholder="Select status"
                        />
                    </div>
                </div>

                <!-- Location -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                        Location
                    </label>
                    <TextInput
                        v-model="formData.location"
                        type="text"
                        placeholder="Enter location"
                        size="md"
                    />
                </div>

                <!-- Description -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                        Description
                    </label>
                    <textarea
                        v-model="formData.description"
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        rows="4"
                        placeholder="Enter job description"
                    ></textarea>
                </div>

                <div class="grid grid-cols-2 gap-4">
                    <!-- Staffing Plan -->
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">
                            Staffing Plan
                        </label>
                        <TextInput
                            v-model="formData.staffing_plan"
                            type="text"
                            placeholder="Enter staffing plan"
                            size="md"
                        />
                    </div>

                    <!-- Planned Vacancies -->
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">
                            Planned Vacancies
                        </label>
                        <TextInput
                            v-model.number="formData.planned_vacancies"
                            type="number"
                            placeholder="Number of planned vacancies"
                            size="md"
                        />
                    </div>
                </div>

                <!-- Salary Range -->
                <div class="border-t pt-4">
                    <h3 class="text-sm font-semibold text-gray-900 mb-3">Salary Range</h3>
                    
                    <div class="grid grid-cols-3 gap-4">
                        <!-- Currency -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">
                                Currency
                            </label>
                            <Select
                                v-model="formData.currency"
                                :options="currencyOptions"
                                placeholder="Select currency"
                            />
                        </div>

                        <!-- Lower Range -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">
                                Lower Range
                            </label>
                            <TextInput
                                v-model.number="formData.lower_range"
                                type="number"
                                placeholder="Min salary"
                                size="md"
                            />
                        </div>

                        <!-- Upper Range -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">
                                Upper Range
                            </label>
                            <TextInput
                                v-model.number="formData.upper_range"
                                type="number"
                                placeholder="Max salary"
                                size="md"
                            />
                        </div>
                    </div>

                    <div class="grid grid-cols-3 gap-4 mt-4">
                        <!-- Salary Per -->
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">
                                Salary Per
                            </label>
                            <Select
                                v-model="formData.salary_per"
                                :options="salaryPerOptions"
                                placeholder="Select period"
                            />
                        </div>
                    </div>
                </div>

                <!-- Pipeline -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                        Custom Pipeline
                    </label>
                    <TextInput
                        v-model="formData.custom_pipeline"
                        type="text"
                        placeholder="Enter pipeline name"
                        size="md"
                    />
                </div>

                <!-- Checkboxes -->
                <div class="border-t flex gap-5 items-center pt-4">
                    <Checkbox
                        v-model="formData.publish"
                        label="Publish on careers page"
                        size="sm"
                    />
                    <Checkbox
                        v-model="formData.publish_salary_range"
                        label="Publish salary range"
                        size="sm"
                    />
                    <Checkbox
                        v-model="formData.publish_applications_received"
                        label="Publish applications received"
                        size="sm"
                    />
                </div>
            </div>

            <!-- Parsed Document Form -->
            <div v-else-if="mode === 'parsed-document'" class="space-y-6 overflow-y-auto h-[70vh]">
                <!-- Sections -->
                <div class="border-t pt-4">
                    <div class="flex justify-between items-center mb-4">
                        <h3 class="text-sm font-semibold text-gray-900">Sections</h3>
                        <Button
                            variant="outline"
                            @click="addSection"
                            size="sm"
                        >
                            Add Section
                        </Button>
                    </div>

                    <div v-for="(section, index) in parsedDocFormData.sections" :key="index" class="mb-6 p-4 border rounded-lg">
                        <div class="flex justify-between items-start mb-3">
                            <h4 class="text-sm font-medium text-gray-900">Section {{ index + 1 }}</h4>
                            <Button
                                variant="ghost"
                                @click="removeSection(index)"
                                size="sm"
                            >
                                Remove
                            </Button>
                        </div>

                        <!-- Section Title -->
                        <div class="mb-3">
                            <label class="block text-sm font-medium text-gray-700 mb-1">
                                Title
                            </label>
                            <TextInput
                                v-model="section.title"
                                type="text"
                                placeholder="Section title"
                                size="md"
                            />
                        </div>

                        <!-- Section Description -->
                        <div class="mb-3">
                            <label class="block text-sm font-medium text-gray-700 mb-1">
                                Description
                            </label>
                            <textarea
                                v-model="section.description"
                                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                                rows="3"
                                placeholder="Section description"
                            ></textarea>
                        </div>

                        <!-- Bullet Points -->
                        <div>
                            <div class="flex justify-between items-center mb-2">
                                <label class="block text-sm font-medium text-gray-700">
                                    Bullet Points
                                </label>
                                <Button
                                    variant="ghost"
                                    @click="addBulletPoint(index)"
                                    size="sm"
                                >
                                    Add Point
                                </Button>
                            </div>
                            <div v-for="(point, pointIndex) in section.pullet_points" :key="pointIndex" class="flex gap-2 mb-2">
                                <TextInput
                                    v-model="section.pullet_points[pointIndex]"
                                    type="text"
                                    placeholder="Bullet point"
                                    size="md"
                                    class="flex-1"
                                />
                                <Button
                                    variant="ghost"
                                    @click="removeBulletPoint(index, pointIndex)"
                                    size="sm"
                                >
                                    ×
                                </Button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </template>

        <template #actions>
            <div class="flex justify-between items-center w-full">
                <div class="flex gap-2">
                    <Button
                        variant="solid"
                        @click="show = false"
                        :disabled="isSaving"
                    >
                        Cancel
                    </Button>
                    <Button
                        v-if="mode === 'job'"
                        variant="outline"
                        @click="switchToParsedDocMode"
                        :disabled="isSaving"
                    >
                        Edit Parsed Document
                    </Button>
                    <Button
                        v-else
                        variant="outline"
                        @click="mode = 'job'"
                        :disabled="isSaving"
                    >
                        Back to Job Edit
                    </Button>
                </div>
                <Button
                    variant="solid"
                    @click="mode === 'job' ? handleSave() : handleSaveParsedDoc()"
                    :loading="isSaving"
                    :disabled="mode === 'job' ? !isFormValid : false"
                >
                    {{ isSaving ? 'Saving...' : 'Save Changes' }}
                </Button>
            </div>
        </template>
    </Dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { Dialog, TextInput, Select, Checkbox, Button } from 'frappe-ui';
import { useToast } from 'vue-toastification';
import { JobDetailsAPI } from '../../api/apiClient.js';

const props = defineProps({
    modelValue: {
        type: Boolean,
        required: true,
    },
    jobName: {
        type: String,
        default: null,
    },
});

const emit = defineEmits(['update:modelValue', 'saved']);

const toast = useToast();

// Dialog visibility
const show = computed({
    get: () => props.modelValue,
    set: (val) => emit('update:modelValue', val),
});

// State
const isLoading = ref(false);
const isSaving = ref(false);
const loadError = ref(null);
const mode = ref('job'); // 'job' or 'parsed-document'

// Form data
const formData = ref({
    name: '',
    job_title: '',
    vacancies: 1,
    status: 'Open',
    description: '',
    department: '',
    employment_type: 'Full-time',
    location: '',
    staffing_plan: '',
    planned_vacancies: 1,
    publish: true,
    publish_salary_range: false,
    publish_applications_received: false,
    currency: 'USD',
    lower_range: 0,
    upper_range: 0,
    salary_per: 'Month',
    custom_pipeline: 'Main',
});

// Parsed document form data
const parsedDocFormData = ref({
    file: '',
    file_hash: '',
    parent_type: 'Job Application',
    parent_id: '',
    meta_data: '{}',
    sections: [],
});

// Options for dropdowns
const employmentTypeOptions = [
    { label: 'Full-time', value: 'Full-time' },
    { label: 'Part-time', value: 'Part-time' },
    { label: 'Contract', value: 'Contract' },
    { label: 'Internship', value: 'Internship' },
    { label: 'Remote', value: 'Remote' },
];

const statusOptions = [
    { label: 'Open', value: 'Open' },
    { label: 'Closed', value: 'Closed' },
    { label: 'On Hold', value: 'On Hold' },
];

const currencyOptions = [
    { label: 'USD', value: 'USD' },
    { label: 'EUR', value: 'EUR' },
    { label: 'GBP', value: 'GBP' },
    { label: 'SAR', value: 'SAR' },
    { label: 'EGP', value: 'EGP' },
];

const salaryPerOptions = [
    { label: 'Month', value: 'Month' },
    { label: 'Year', value: 'Year' },
    { label: 'Hour', value: 'Hour' },
];

// Form validation
const isFormValid = computed(() => {
    return formData.value.job_title && formData.value.vacancies > 0;
});

// Watch for dialog open and job name changes
watch([() => props.modelValue, () => props.jobName], ([isOpen, jobName]) => {
    if (isOpen && jobName) {
        loadJobData(jobName);
    }
});

// Load job data from API
async function loadJobData(jobName) {
    isLoading.value = true;
    loadError.value = null;

    try {
        const response = await JobDetailsAPI.findJobOpening(jobName);
        console.log(response);
        
        if (response) {
            const job = response;
            
            // Map API response to form data
            formData.value = {
                name: job.name || '',
                job_title: job.designation || '',
                vacancies: 1, // Not in response, keeping default
                status: 'Open', // Not in response, keeping default
                description: extractDescription(job.parsed_documents),
                department: job.department || '',
                employment_type: job.employment_type || 'Full-time',
                location: job.location || '',
                staffing_plan: '', // Not in response
                planned_vacancies: 1, // Not in response
                publish: job.publish === true || job.publish === 1 ? true : false,
                publish_salary_range: job.publish_salary_range === true || job.publish_salary_range === 1 ? true : false,
                publish_applications_received: job.publish_applications_received === true || job.publish_applications_received === 1 ? true : false,
                currency: job.currency || 'USD',
                lower_range: parseFloat(job.lower_range) || 0,
                upper_range: parseFloat(job.upper_range) || 0,
                salary_per: job.salary_per || 'Month',
                custom_pipeline: 'Main', // Not in response, keeping default
            };

            // Populate parsed document form if available
            if (job.parsed_documents && Array.isArray(job.parsed_documents) && job.parsed_documents.length > 0) {
                const parsedDoc = job.parsed_documents[0];
                parsedDocFormData.value = {
                    file: parsedDoc.file || parsedDoc.document_id || '',
                    file_hash: parsedDoc.file_hash || '',
                    parent_type: 'Job Opening',
                    parent_id: job.name || '',
                    meta_data: typeof parsedDoc.meta_data === 'string' ? parsedDoc.meta_data : JSON.stringify(parsedDoc.meta_data || {}),
                    sections: (parsedDoc.sections || []).map(section => ({
                        title: section.title || '',
                        description: section.description || '',
                        pullet_points: Array.isArray(section.pullet_points) 
                            ? section.pullet_points 
                            : (typeof section.pullet_points === 'string' 
                                ? JSON.parse(section.pullet_points) 
                                : [])
                    })),
                };
            }
        }
    } catch (error) {
        console.error('Failed to load job data:', error);
        loadError.value = error.message || 'Failed to load job data';
        toast.error(`Failed to load job data: ${error.message || 'Unknown error'}`);
    } finally {
        isLoading.value = false;
    }
}

// Extract description from parsed documents
function extractDescription(parsedDocuments) {
    if (!parsedDocuments || !Array.isArray(parsedDocuments) || parsedDocuments.length === 0) {
        return '';
    }

    let description = '';
    const doc = parsedDocuments[0];
    
    if (doc.sections && Array.isArray(doc.sections)) {
        doc.sections.forEach((section) => {
            if (section.title) {
                description += `**${section.title}**\n\n`;
            }
            if (section.description) {
                description += `${section.description}\n\n`;
            }
        });
    }

    return description.trim();
}

// Handle save
async function handleSave() {
    if (!isFormValid.value) {
        toast.error('Please fill in all required fields');
        return;
    }

    isSaving.value = true;

    try {
        // Prepare payload
        const payload = {
            name: formData.value.name,
            vacancies: formData.value.vacancies,
            job_title: formData.value.job_title,
            status: formData.value.status,
            description: formData.value.description,
            department: formData.value.department,
            employment_type: formData.value.employment_type,
            location: formData.value.location,
            staffing_plan: formData.value.staffing_plan,
            planned_vacancies: formData.value.planned_vacancies,
            publish: formData.value.publish ? 1 : 0,
            publish_applications_received: formData.value.publish_applications_received ? 1 : 0,
            currency: formData.value.currency,
            lower_range: parseFloat(formData.value.lower_range) || 0.0,
            upper_range: parseFloat(formData.value.upper_range) || 0.0,
            salary_per: formData.value.salary_per,
            publish_salary_range: formData.value.publish_salary_range ? 1 : 0,
            custom_pipeline: formData.value.custom_pipeline,
        };

        // Call the API to create/update job
        const response = await JobDetailsAPI.createOrUpdateJobOpening(payload);
        toast.success('Job updated successfully!');
        emit('saved', response.message);
        show.value = false;
    } catch (error) {
        console.error('Failed to save job:', error);
        toast.error(`Failed to save job: ${error.message || 'Unknown error'}`);
    } finally {
        isSaving.value = false;
    }
}

// Switch to parsed document mode
function switchToParsedDocMode() {
    mode.value = 'parsed-document';
}

// Add new section to parsed document
function addSection() {
    parsedDocFormData.value.sections.push({
        title: '',
        description: '',
        pullet_points: []
    });
}

// Remove section from parsed document
function removeSection(index) {
    parsedDocFormData.value.sections.splice(index, 1);
}

// Add bullet point to section
function addBulletPoint(sectionIndex) {
    parsedDocFormData.value.sections[sectionIndex].pullet_points.push('');
}

// Remove bullet point from section
function removeBulletPoint(sectionIndex, pointIndex) {
    parsedDocFormData.value.sections[sectionIndex].pullet_points.splice(pointIndex, 1);
}

// Handle save parsed document
async function handleSaveParsedDoc() {
    isSaving.value = true;

    try {
        // Prepare payload
        const payload = {
            file: parsedDocFormData.value.file,
            file_hash: parsedDocFormData.value.file_hash,
            parent_type: parsedDocFormData.value.parent_type,
            parent_id: parsedDocFormData.value.parent_id,
            sections: parsedDocFormData.value.sections.map(section => ({
                title: section.title,
                description: section.description,
                pullet_points: section.pullet_points
            }))
        };

        console.log('Parsed Document Payload:', { payload });
        
        const response = await JobDetailsAPI.createOrUpdateParsedDocument(payload);
        console.log('Parsed document response:', response);
        
        toast.success('Parsed document updated successfully!');
        emit('saved');
        show.value = false;
    } catch (error) {
        console.error('Failed to save parsed document:', error);
        toast.error(`Failed to save parsed document: ${error.message || 'Unknown error'}`);
    } finally {
        isSaving.value = false;
    }
}
</script>

<style scoped>
textarea {
    resize: vertical;
}
</style>
