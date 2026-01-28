<template>
    <div class="jc-page">
        <!-- Toolbar with search and filters -->

        <!-- <div class="flex justify-end w-full my-4 px-1">
      <Button theme="gray" variant="solid" size="md" class="w-48" @click="createNewJob">
        + New Job
      </Button>
    </div> -->
        <div class="jc-toolbar">
            <div class="jc-search">
                <TextInput
                    v-model="filters.search"
                    type="text"
                    size="sm"
                    variant="subtle"
                    placeholder="Start typing to search jobs..."
                    @input="debouncedApplyFilters"
                />
            </div>

            <div class="jc-filters">
                <Select
                    class="w-48"
                    placeholder="Select Department"
                    v-model="filters.department"
                    :options="departmentOptions"
                    @change="applyFilters"
                />

                <Select
                    class="w-48"
                    placeholder="Select Location"
                    v-model="filters.location"
                    :options="locationOptions"
                    @change="applyFilters"
                />

                <Select
                    class="w-48"
                    placeholder="Select Group"
                    v-model="filters.group"
                    :options="groupOptions"
                    @change="applyFilters"
                />

                <Checkbox
                    size="sm"
                    v-model="filters.includeDrafts"
                    label="Include draft jobs"
                    @change="applyFilters"
                />
                <!--
      <Button theme="gray" variant="solid" size="md" class="w-32" @click="createNewJob">
        New Job
      </Button> -->
            </div>
        </div>

        <div class="flex justify-end gap-3 items-center w-full my-4">
            <Button
                theme="gray"
                size="md"
                class="w-40"
                :disabled="jobsResource.loading"
                @click="reload"
            >
                {{ jobsResource.loading ? "Refreshing..." : "Refresh" }}
            </Button>
            <Button theme="gray" variant="solid" size="md" class="w-40" @click="createNewJob">
                New Job
            </Button>
        </div>

        <!-- Loading state -->
        <div v-if="jobsResource.loading" class="text-center py-8 text-gray-500">
            Loading jobs...
        </div>

        <!-- Error state -->
        <div v-else-if="jobsResource.error" class="text-center py-8 text-red-500">
            Error loading jobs: {{ jobsResource.error }}
        </div>

        <!-- Jobs list -->
        <div v-else-if="filteredJobs.length > 0" class="jc-list">
            <div v-for="job in filteredJobs" :key="job.name" class="jc-card" :data-job="job.name">
                <!-- Card Header -->
                <div class="jc-card-head">
                    <div>
                        <div class="jc-title" @click="openJob(job.name)">
                            {{ job.title }}
                        </div>
                        <div class="jc-subtitle">
                            {{ job.department }} · {{ job.work_mode }} · {{ job.location }}
                        </div>
                    </div>

                    <div class="jc-actions">
                        <button class="btn btn-default btn-sm" @click="copyJobLink(job)">
                             Copy Link
                        </button>
                        <button class="btn btn-default !bg-black !text-white !px-5 btn-sm" @click="editJob(job.name)">
                             Edit Job
                        </button>
                    </div>
                </div>

                <!-- Pipeline stages -->
                <div v-if="job.stages.length > 0" class="jc-pipeline">
                    <div
                        v-for="stage in job.stages.slice(0, 12)"
                        :key="`${job.name}-${stage.id}`"
                        class="jc-stage"
                        :title="stage.label"
                    >
                        <div class="jc-stage-count">{{ formatCount(stage.count) }}</div>
                        <div class="jc-stage-label">{{ stage.label }}</div>
                    </div>
                </div>

                <!-- Card Footer -->
                <div class="jc-card-foot">
                    <div v-if="!job.is_published" class="jc-warn">
                        <span style="font-size: 16px">✕</span>
                        <span
                            >This job is not published on your careers page or on any job
                            boards</span
                        >
                    </div>
                    <div v-else></div>

                    <div>
                        Candidates: {{ job.candidates_total }} total ·
                        {{ job.candidates_active }} active in pipeline · Last candidate on
                        {{ formatDate(job.last_candidate_on) }}
                    </div>
                </div>
            </div>
        </div>

        <!-- Empty state -->
        <div v-else class="jc-empty">No jobs found.</div>

        <!-- File input for job upload -->
        <input
            ref="jobFileInput"
            type="file"
            accept=".pdf,.doc,.docx"
            style="display: none"
            @change="handleJobFileUpload"
        />

        <!-- Job Description Dialog -->
        <JobDescriptionDialog
            v-model="showJobDialog"
            :parsed-data="parsedJobData"
            :is-loading="isParsing"
            @create="handleJobCreate"
        />

        <!-- Edit Job Dialog -->
        <EditJobDialog
            v-model="showEditDialog"
            :job-name="selectedJobName"
            @saved="handleJobSaved"
        />
    </div>
</template>

<script setup>
import { createResource, TextInput, Select, Checkbox, Button } from "frappe-ui";
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import { useToast } from "vue-toastification";
import { JobDetailsAPI } from "../../api/apiClient.js";
import JobDescriptionDialog from "../../components/jobs/JobDescriptionDialog.vue";
import EditJobDialog from "../../components/jobs/EditJobDialog.vue";

const router = useRouter();
const toast = useToast();

JobDetailsAPI.init(createResource);

// State
const filters = ref({
    search: "",
    department: "",
    location: "",
    group: "",
    includeDrafts: true,
});

const allJobs = ref([]);
const filteredJobs = ref([]);

// File upload and parsing state
const jobFileInput = ref(null);
const isUploading = ref(false);
const uploadProgress = ref(0);
const isParsing = ref(false);
const showJobDialog = ref(false);
const parsedJobData = ref(null);

// Edit job state
const showEditDialog = ref(false);
const selectedJobName = ref(null);

// Fetch jobs from API
const jobsResource = createResource({
    url: "mawhub.job_opening_list",
    auto: true,
    onSuccess(data) {
        allJobs.value = transformJobData(data || []);
        applyFilters();
    },
});

// Transform API response to UI format
function transformJobData(rawJobs) {
    return rawJobs.map((job) => {
        // Get unique steps and aggregate candidate counts
        const stepsMap = new Map();

        if (job.steps && Array.isArray(job.steps)) {
            job.steps.forEach((step) => {
                const key = `${step.step_id}-${step.step_name}`;
                if (!stepsMap.has(key)) {
                    stepsMap.set(key, {
                        id: step.step_id,
                        label: step.step_name,
                        count: 0,
                    });
                }
                stepsMap.get(key).count += step.candidate_count || 0;
            });
        }

        const stages = Array.from(stepsMap.values()).sort((a, b) => a.id - b.id);

        // Calculate total candidates
        const totalCandidates = parseInt(job.candidate_count) || 0;

        // Determine publish status
        const isPublished = job.publish === 1;
        const isDraft = job.docstatus === 0;

        return {
            name: job.name,
            title: job.designation || "Untitled Position",
            department: job.department || "Not Specified",
            location: job.location || "Not Specified",
            work_mode: job.employment_type || "Full-time",
            is_published: isPublished,
            is_draft: isDraft,
            route: job.route || "",
            stages: stages,
            candidates_total: totalCandidates,
            candidates_active: totalCandidates,
            last_candidate_on: job.posted_on,
            group: job.department || null,
        };
    });
}

// Computed properties for filter options
const departments = computed(() => {
    return [...new Set(allJobs.value.map((j) => j.department).filter(Boolean))].sort();
});

const locations = computed(() => {
    return [...new Set(allJobs.value.map((j) => j.location).filter(Boolean))].sort();
});

const groups = computed(() => {
    return [...new Set(allJobs.value.map((j) => j.group).filter(Boolean))].sort();
});

// Format options for Select components
const departmentOptions = computed(() => [
    { label: "All departments", value: "" },
    ...departments.value.map((dept) => ({ label: dept, value: dept })),
]);

const locationOptions = computed(() => [
    { label: "All locations", value: "" },
    ...locations.value.map((loc) => ({ label: loc, value: loc })),
]);

const groupOptions = computed(() => [
    { label: "No group applied", value: "" },
    ...groups.value.map((grp) => ({ label: grp, value: grp })),
]);

// Apply filters
function applyFilters() {
    const f = filters.value;

    filteredJobs.value = allJobs.value.filter((j) => {
        // Filter drafts
        if (!f.includeDrafts && j.is_draft) return false;

        // Filter by department
        if (f.department && j.department !== f.department) return false;

        // Filter by location
        if (f.location && j.location !== f.location) return false;

        // Filter by group
        if (f.group && j.group !== f.group) return false;

        // Filter by search query
        if (f.search) {
            const query = f.search.toLowerCase();
            const searchText =
                `${j.title} ${j.department} ${j.location} ${j.work_mode}`.toLowerCase();
            if (!searchText.includes(query)) return false;
        }

        return true;
    });
}

// Debounced filter for search input
let debounceTimeout = null;
function debouncedApplyFilters() {
    clearTimeout(debounceTimeout);
    debounceTimeout = setTimeout(applyFilters, 200);
}

// Format count for display
function formatCount(count) {
    if (count >= 1000) {
        return `${(count / 1000).toFixed(1)}k`;
    }
    return count.toString();
}

// Format date for display
function formatDate(dateStr) {
    if (!dateStr) return "N/A";
    try {
        const date = new Date(dateStr);
        return date.toLocaleDateString("en-US", {
            year: "numeric",
            month: "short",
            day: "numeric",
        });
    } catch {
        return dateStr;
    }
}

// Action handlers
function openJob(jobName) {
    // Navigate to job details page
    router.push({ name: "JobDetails", params: { jobId: jobName } });
}

function copyJobLink(job) {
    // const jobLink = `${window.location.origin}/jobs/mawhub/${jobName}`;
    const jobLink = `http://localhost:8001/${job.route}`;
    navigator.clipboard
        .writeText(jobLink)
        .then(() => {
            toast.success("Job link copied to clipboard!");
        })
        .catch(() => {
            toast.error("Failed to copy link");
        });
}

function editJob(jobName) {
    selectedJobName.value = jobName;
    showEditDialog.value = true;
}

function createNewJob() {
    if (jobFileInput.value) {
        jobFileInput.value.click();
    }
}

async function handleJobFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file type
    const validTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    if (!validTypes.includes(file.type)) {
        toast.error('Please upload a PDF or Word document');
        return;
    }

    // Validate file size (max 10MB)
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
        toast.error('File size must be less than 10MB');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('is_private', 1);

    try {
        isUploading.value = true;
        uploadProgress.value = 0;

        const response = await fetch('/api/method/upload_file', {
            method: 'POST',
            headers: {
                'X-Frappe-CSRF-Token': window.frappe?.csrf_token || '',
            },
            body: formData
        });

        if (!response.ok) {
            throw new Error('Upload failed');
        }

        const result = await response.json();
        
        if (result.message && result.message.file_url) {
            uploadProgress.value = 100;
            toast.success('Job description uploaded successfully');
            console.log('File Uploaded:', result.message.file_url);
            
            // Parse the job description
            await parseJobDescription(result.message.file_url, result.message.name);
        } else {
            throw new Error('Invalid response from server');
        }
    } catch (error) {
        console.error('Upload failed:', error);
        toast.error(`Upload failed: ${error.message || 'Unknown error'}`);
    } finally {
        isUploading.value = false;
        uploadProgress.value = 0;
        // Reset file input
        if (jobFileInput.value) {
            jobFileInput.value.value = '';
        }
    }
}

async function parseJobDescription(fileUrl, fileName) {
    try {
        toast.info('Parsing job description...');
        
        // Initialize empty parsed data
        parsedJobData.value = {};
        
        // Set loading state to true
        isParsing.value = true;
        
        // Open the dialog to show real-time parsing
        showJobDialog.value = true;
        
        // Call the job opening parse API with progress callback
        const response = await JobDetailsAPI.parseJobOpening(
            {
                path: `./${import.meta.env.VITE_SITE_NAME}${fileUrl}`,
                file_name: fileName,
            },
            (progressData) => {
                // Handle progress updates from the EventStream
                console.log('Job parsing step:', progressData);

                if(progressData && progressData.event == 'error') {
                    toast.error(`Job parsing error: ${progressData.data || 'Unknown error'}`);
                    isParsing.value = false;
                    showJobDialog.value = false;
                    // parsedJobData.value = null;
                    return
                };
                if(!progressData || !progressData.data) return;
                if(!progressData || !progressData.data) return;
                isParsing.value = false;
                if(progressData.event == 'final'){
                    toast.success('Job description parsed successfully!');
                    // parsedJobData.value = progressData.data
                    return;
                }
                // Update the parsed data in real-time
                if(progressData.data.titles){
                    progressData.data.titles.forEach(title => {
                        if(!parsedJobData.value[title]){
                            parsedJobData.value[title] = {
                                description: '',
                                bullet_points: []
                            };
                        }
                    });
                    return
                }
                parsedJobData.value[Object.keys(progressData.data)[0]] = progressData.data[Object.keys(progressData.data)[0]];
                console.log('parsedJobData:', parsedJobData.value);
            }
        );
    } catch (error) {
        console.error('Job parsing failed:', error);
        toast.error(`Job parsing failed: ${error.message || 'Unknown error'}`);
        showJobDialog.value = false;
        parsedJobData.value = null;
    } finally {
        // Set loading state to false when parsing ends
        // isParsing.value = false;
    }
}

// Handle job creation
function handleJobCreate(parsedData) {
    // Reload the jobs list after creating a new job
    reload();
}

// Handle job saved
function handleJobSaved(updatedJob) {
    // Reload the jobs list after updating a job
    reload();
}

// Reload function (can be called externally)
function reload() {
    jobsResource.fetch();
}

// Expose reload function
defineExpose({ reload });
</script>

<style>
.jc-page {
    padding: 3rem;
}

.jc-toolbar {
    display: flex;
    gap: 12px;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    margin-bottom: 16px;
}

.jc-search {
    min-width: 480px;
}

.jc-filters {
    display: flex;
    gap: 10px;
    align-items: center;
}
.jc-filters label {
    width: 120px !important;
}

.jc-list {
    display: flex;
    flex-direction: column;
    gap: 14px;
}

.jc-card {
    background: var(--card-bg, #fff);
    border: 1px solid var(--border-color, #e6e6e6);
    border-radius: 10px;
    padding: 16px;
}

.jc-card-head {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 12px;
}

.jc-title {
    font-size: 18px;
    font-weight: 700;
    margin: 0;
    cursor: pointer;
}

.jc-title:hover {
    color: #0066cc;
}

.jc-subtitle {
    color: #6b7280;
    margin-top: 4px;
    font-size: 13px;
}

.jc-actions {
    display: flex;
    gap: 10px;
    align-items: center;
}

.jc-pipeline {
    display: grid;
    grid-template-columns: repeat(12, minmax(70px, 1fr));
    gap: 10px;
    margin-top: 14px;
    padding-top: 14px;
    border-top: 1px solid var(--border-color, #eee);
    overflow-x: auto;
}

.jc-stage {
    text-align: center;
    border-right: 1px solid #f0f0f0;
    padding-right: 10px;
}

.jc-stage:last-child {
    border-right: none;
}

.jc-stage-count {
    font-size: 18px;
    font-weight: 700;
}

.jc-stage-label {
    font-size: 12px;
    color: #6b7280;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.jc-card-foot {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    align-items: center;
    margin-top: 12px;
    color: #6b7280;
    font-size: 13px;
}

.jc-warn {
    color: #b42318;
    display: inline-flex;
    align-items: center;
    gap: 8px;
}

.jc-empty {
    padding: 18px;
    color: #6b7280;
    text-align: center;
}

/* Form controls styling */
.form-control {
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

/* Button styling */
.btn {
    padding: 8px 16px;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    border: 1px solid transparent;
    transition: all 0.2s;
    white-space: nowrap;
}

.btn-default {
    background: white;
    border-color: #d1d5db;
    color: #374151;
}

.btn-default:hover {
    background: #f9fafb;
    border-color: #9ca3af;
}

.btn-primary {
    background: #3b82f6;
    color: white;
}

.btn-primary:hover {
    background: #2563eb;
}

.btn-sm {
    padding: 6px 12px;
    font-size: 13px;
}
</style>
