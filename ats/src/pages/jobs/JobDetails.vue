<template>
    <div class="jd-page">
        <!-- Loading state -->
        <!-- <div v-if="jobDetailsResource.loading" class="jd-loading">
            <div class="text-center py-8 text-gray-500">Loading job details...</div>
        </div> -->

        <!-- Error state -->
        <!-- <div v-else-if="jobDetailsResource.error" class="jd-error">
            <div class="text-center py-8 text-red-500">
                Error loading job details: {{ jobDetailsResource.error }}
            </div>
        </div> -->

        <!-- Header -->
        <div class="jd-content">
            <div class="jd-header">
                <div>
                    <div class="jd-title-row">
                        <h2 class="jd-title">{{ job?.designation || "Job Details" }}</h2>
                        <div style="display: flex; gap: 8px;">
                            <Button size="sm" @click="showJobDescription">
                                <Eye :size="16" class="button-icon" />
                                Show
                            </Button>
                            <Button size="sm" @click="editJob">
                                <Edit2 :size="16" class="button-icon" />
                                Edit
                            </Button>
                        </div>
                    </div>
                    <!-- <div class="jd-subtitle">
                        {{ job?.department }} · {{ job?.work_mode }} · {{ job?.location }}
                    </div> -->
                </div>

                <div class="jd-header-actions">
                    <input
                        ref="resumeFileInput"
                        type="file"
                        accept=".pdf,.doc,.docx"
                        style="display: none"
                        @change="handleResumeUpload"
                    />
                    <Button
                        theme="gray"
                        class="w-40 p-5"
                        :loading="isUploading"
                        @click="triggerResumeUpload"
                    >
                        <Upload :size="16" class="button-icon" v-if="!isUploading" />
                        {{ isUploading ? `Uploading... ${uploadProgress}%` : "Upload Resume" }}
                    </Button>
                    <Button
                        theme="gray"
                        :variant="'solid'"
                        class="w-40 p-5 p-5"
                        @click="showAddCandidateDialog = true"
                    >
                        <UserPlus :size="16" class="button-icon" />
                        Add candidates
                    </Button>
                </div>
            </div>

            <!-- Pipeline tabs -->
            <div class="jd-pipeline-container">
                <div class="jd-pipeline">
                    <div
                        v-for="step in Object.values(steps)"
                        :key="step.step_id"
                        :class="['jd-step', { active: activeStep === step.step_id }]"
                        @click="changeStep(step.step_id)"
                    >
                        {{ step.step_name }} <span class="count">{{ step.candidate_count }}</span>
                    </div>
                </div>
                <Button size="sm" theme="gray" @click="editPipeline">
                    <Settings :size="16" class="button-icon" />
                    Edit Pipeline
                </Button>
            </div>

            <!-- Body -->
            <div class="jd-body">
                <!-- Left: list -->
                <div class="jd-left">
                    <div class="jd-left-top">
                        <TextInput
                            v-model="searchQuery"
                            type="text"
                            size="sm"
                            variant="subtle"
                            placeholder="Search by name, skills, tags..."
                        />
                        <div class="jd-bulk-toolbar">
                            <Button size="sm" @click="toggleSelectAll">
                                <CheckSquare :size="16" class="button-icon" v-if="!allSelected" />
                                <Square :size="16" class="button-icon" v-else />
                                {{ allSelected ? "Deselect All" : "Select All" }}
                            </Button>
                            <div v-if="selectedCandidates.size > 0" class="jd-bulk-actions">
                                <Button
                                    size="sm"
                                    theme="gray"
                                    :variant="'solid'"
                                    @click="showBulkMoveDialog = true"
                                >
                                    <MoveRight :size="16" class="button-icon" />
                                    Bulk Move
                                </Button>
                                <Button size="sm" @click="clearSelection">
                                    <X :size="16" class="button-icon" />
                                    Clear
                                </Button>
                            </div>
                        </div>
                    </div>
                    <div class="jd-candidate-list">
                        <div
                            v-for="candidate in steps[activeStep]?.candidates || []"
                            :key="candidate.applicant_id"
                            :class="['jd-item', { active: activeCandidateId === candidate.applicant_id }]"
                            @click="selectCandidate(candidate.applicant_id)"
                        >
                            <input
                                type="checkbox"
                                class="jd-candidate-checkbox"
                                :checked="selectedCandidates.has(candidate.applicant_id)"
                                @click.stop="toggleCandidateSelection(candidate.applicant_id)"
                            />
                            <div class="jd-avatar">
                                {{ candidate.applicant_name?.charAt(0).toUpperCase() }}
                            </div>
                            <div>
                                <div class="jd-item-name">{{ candidate.applicant_name }}</div>
                                <div v-if="candidate.applicant_source" class="jd-item-sub">
                                    via <b>{{ candidate.applicant_source }}</b>
                                    <!-- {{ formatDate(candidate.applicant_created_at) }} -->
                                </div>
                            </div>
                        </div>
                        <div
                            v-if="filteredCandidates.length === 0"
                            class="text-muted"
                            style="padding: 10px"
                        >
                            No candidates
                        </div>
                    </div>
                </div>

                <!-- Middle: details -->
                <div class="jd-middle">
                    <div class="jd-detail-card">
                        <div v-if="!activeCandidate" class="text-muted py-10">
                            Select a candidate from the list.
                        </div>
                        <div v-else>
                            <div class="jd-detail-head">
                                <div style="display: flex; align-items: center; gap: 12px">
                                    <div
                                        class="jd-avatar"
                                        style="width: 55px; height: 55px; font-size: 20px"
                                    >
                                        {{ activeCandidate.applicant_name?.charAt(0).toUpperCase() }}
                                    </div>
                                    <div>
                                        <h3 class="jd-detail-name">{{ activeCandidate.applicant_name }}</h3>
                                        <div class="jd-detail-meta">
                                            <a
                                                class="underline"
                                                :href="`mailto:${activeCandidate.applicant_email}`"
                                                >{{ activeCandidate.applicant_email }}</a
                                            >
                                        </div>
                                    </div>
                                </div>
                                <div
                                    style="
                                        display: flex;
                                        flex-direction: column;
                                        gap: 8px;
                                        min-width: 200px;
                                    "
                                >
                                    <Select
                                        v-model="targetStep"
                                        :options="stepOptions"
                                        placeholder="Select step"
                                    />
                                    <Button
                                        size="sm"
                                        theme="gray"
                                        :variant="'solid'"
                                        @click="moveCandidateToStep"
                                    >
                                        <MoveRight :size="16" class="button-icon" />
                                        Move to selected step
                                    </Button>
                                </div>
                            </div>

                            <!-- Tab Navigation -->
                            <div class="jd-tabs-nav">
                                <button
                                    v-for="tab in tabs"
                                    :key="tab.key"
                                    :class="['jd-tab-button', { active: activeTab === tab.key }]"
                                    @click="activeTab = tab.key"
                                >
                                    {{ tab.label }}
                                </button>
                            </div>

                            <!-- Tab Content -->
                            <div class="jd-tab-content">
                                <component
                                    :is="tabComponents[activeTab]"
                                    :candidate="activeCandidate"
                                    :job-title="job?.designation"
                                />
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Right: action panel -->
                <div class="jd-actions-panel !w-[12rem]">
                    <div v-if="!activeCandidate" class="text-muted py-10">Select a candidate</div>
                    <div v-else class="jd-actions-content">
                        <h4 class="jd-actions-title">Actions</h4>
                        <div class="jd-actions-buttons">
                            <Button
                                v-for="action in candidateActions"
                                :key="action.key"
                                size="sm"
                                theme="gray"
                                class="p-7"
                                :variant="action.variant === 'danger' ? 'outline' : 'solid'"
                                @click="action.action"
                            >
                                <div :class="['jd-action-button']">
                                    <component
                                        :is="action.icon"
                                        :size="14"
                                        class="jd-action-icon"
                                    />
                                    <span>{{ action.label }}</span>
                                </div>
                            </Button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Dialog Components -->
            <AddCandidateDialog 
                v-model="showAddCandidateDialog" 
                :job-id="job?.name || ''"
                @success="onCandidateAdded" 
            />

            <AssignInterviewDialog
                v-model="showAssignInterviewDialog"
                :candidate-id="activeCandidate?.applicant_id || ''"
                :candidate-name="activeCandidate?.applicant_name || ''"
                :job-id="job?.name || ''"
                :job-designation="job?.designation || ''"
                :resume-link="activeCandidate?.applicant_resume_link || ''"
                @success="onInterviewAssigned"
            />

            <EditJobDialog
                v-model="showEditDialog"
                :job-name="jobId"
                @saved="getJobOpening"
            />
            <JobDescriptionDialog
                v-model="showJobDescriptionDialog"
                :parsed-data="transformedParsedData"
                :is-loading="false"
                :job-details="job"
            />

            <BulkMoveDialog
                v-model="showBulkMoveDialog"
                :step-options="stepOptions"
                :candidate-count="selectedCandidates.size"
                :candidate-ids="Array.from(selectedCandidates)"
                @success="onBulkMoveCompleted"
            />

            <ApplicantProfileDialog
                v-model="showProfileDialog"
                :applicant-id="activeCandidate?.applicant_id"
                :candidate-name="activeCandidate?.applicant_name"
                :profile="parsingProfile || undefined"
                :is-loading="isParsingResume"
                :on-fetch-profile="fetchApplicantProfile"
            />

            <SendEmailDialog
                v-model="showSendEmailDialog"
                :candidate-id="activeCandidate?.applicant_id || ''"
                :candidate-email="activeCandidate?.applicant_email || ''"
                :job-id="job?.name || ''"
                @success="onEmailSent"
            />

            <EditPipelineDialog
                v-model="showEditPipelineDialog"
                :job-id="job?.name || ''"
                :job-data="job"
                @success="onPipelineUpdated"
            />
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import { TextInput, Select, Button, createResource } from "frappe-ui";
import { useToast } from "vue-toastification";
import { JobDetailsAPI } from "../../api/apiClient.js";
import { NewJobDetailsAPI } from "../../api/ApiClient.ts";
import { Edit2, Upload, UserPlus, CheckSquare, Square, MoveRight, X, Calendar, Share2, Printer, Copy, ArrowRightLeft, Trash2, Edit, Settings, Eye,
} from "lucide-vue-next";
import AddCandidateDialog from "../../components/jobs/AddCandidateDialog.vue";
import AssignInterviewDialog from "../../components/jobs/AssignInterviewDialog.vue";
import BulkMoveDialog from "../../components/jobs/BulkMoveDialog.vue";
import ApplicantProfileDialog from "../../components/jobs/ApplicantProfileDialog.vue";
import SendEmailDialog from "../../components/jobs/SendEmailDialog.vue";
import ApplicantProfile from "../../components/jobs/ApplicantProfile.vue";
import ApplicantTimeline from "../../components/jobs/ApplicantTimeline.vue";
import ApplicantCommunication from "../../components/jobs/ApplicantCommunication.vue";
import ApplicantReview from "../../components/jobs/ApplicantReview.vue";
import ApplicantComments from "../../components/jobs/ApplicantComments.vue";
import EditJobDialog from "../../components/jobs/EditJobDialog.vue";
import JobDescriptionDialog from "../../components/jobs/JobDescriptionDialog.vue";
import EditPipelineDialog from "../../components/jobs/EditPipelineDialog.vue";
import type { JobOpeningDTO, JobPipelineStepDTO, JobPipelineStepCandidateDTO, CandidateDTO } from "@/src/tsgen/job_opening.ts";
import type { PipelineStepOption, ResumeParseProgressData, ApplicantParsedProfile,
} from "@/src/types/job-details";

const toast = useToast();
const route = useRoute();

JobDetailsAPI.init(createResource);
NewJobDetailsAPI.init(createResource);

const jobId = computed(() => route.params.jobId as string);

const job = ref<JobOpeningDTO>();
const candidates = ref<CandidateDTO[]>([]);
const steps = ref<Record<string, JobPipelineStepDTO>>({});
const activeStep = ref<string>("All");
const activeCandidateId = ref<string | null>(null);
const selectedCandidates = ref(new Set<string>());
const searchQuery = ref<string>("");
const targetStep = ref<string>("");

const showEditDialog = ref(false);
const showAddCandidateDialog = ref(false);
const showAssignInterviewDialog = ref(false);
const showBulkMoveDialog = ref(false);
const showProfileDialog = ref(false);
const showSendEmailDialog = ref(false);
const showJobDescriptionDialog = ref(false);
const showEditPipelineDialog = ref(false);
const parsingProfile = ref<ApplicantParsedProfile | null>(null);

const activeTab = ref<keyof typeof tabComponents>("profile");

const resumeFileInput = ref<HTMLInputElement | null>(null);
const isUploading = ref(false);
const uploadProgress = ref(0);
const isParsingResume = ref(false);

const tabs: Array<{ key: keyof typeof tabComponents; label: string }> = [
    { key: "profile", label: "Profile" },
    { key: "communication", label: "Communication" },
    { key: "timeline", label: "Timeline" },
    { key: "review", label: "Review" },
    { key: "comments", label: "Comments" },
];

const tabComponents = {
    profile: ApplicantProfile,
    timeline: ApplicantTimeline,
    communication: ApplicantCommunication,
    review: ApplicantReview,
    comments: ApplicantComments,
};

const candidateActions = [
    {
        key: "assign-interview",
        label: "Assign Interview",
        icon: Calendar,
        action: () => {
            showAssignInterviewDialog.value = true;
        },
    },
    {
        key: "share",
        label: "Share Candidate",
        icon: Share2,
        action: shareCandidate,
    },
    {
        key: "print",
        label: "Print Profile",
        icon: Printer,
        action: printProfile,
    },
    {
        key: "copy-job",
        label: "Copy to Job",
        icon: Copy,
        action: copyToJob,
    },
    {
        key: "move-job",
        label: "Move to Job",
        icon: ArrowRightLeft,
        action: moveToJob,
    },
    {
        key: "edit",
        label: "Edit Candidate",
        icon: Edit,
        action: editCandidate,
    },
    {
        key: "delete",
        label: "Delete Candidate",
        icon: Trash2,
        action: deleteCandidate,
        variant: "danger",
    },
];

const stepOptions = computed<PipelineStepOption[]>(() => {
    if (!job.value?.steps) return [];
    return job.value.steps.map((step) => ({
        label: step.step_name,
        value: step.step_id,
    }));
});

const filteredCandidates = computed<JobPipelineStepCandidateDTO[]>(() => {
    return steps.value[activeStep.value]?.candidates || [];
});

const activeCandidate = computed<CandidateDTO | null>(() => {
    if (!activeCandidateId.value) return null;
    return filteredCandidates.value.find((c) => c.applicant_id === activeCandidateId.value) || null;
});

const allSelected = computed(() => {
    const filtered = filteredCandidates.value;
    return filtered.length > 0 && selectedCandidates.value.size === filtered.length;
});

const transformedParsedData = computed(() => {
    if (!job.value?.parsed_documents || job.value.parsed_documents.length === 0) {
        return {};
    }
    const parsedDoc = job.value.parsed_documents[0];
    const transformed: Record<string, any> = {};
    if (parsedDoc.sections && Array.isArray(parsedDoc.sections)) {
        parsedDoc.sections.forEach((section: any) => {
            const key = section.title
                .toLowerCase()
                .replace(/[^a-z0-9]+/g, "_")
                .replace(/^_+|_+$/g, "");

            let bulletPoints: string[] = [];
            if (section.pullet_points) {
                try {
                    bulletPoints =
                        typeof section.pullet_points === "string"
                            ? JSON.parse(section.pullet_points)
                            : section.pullet_points;
                } catch (e) {
                    console.error("Failed to parse bullet points:", e);
                    bulletPoints = [];
                }
            }

            transformed[key] = {
                description: section.description || "",
                bullet_points: Array.isArray(bulletPoints) ? bulletPoints : [],
            };
        });
    }
    return transformed;
});

const getJobOpening = async () => {
    try {
        const data = await NewJobDetailsAPI.findJobOpening(jobId.value);
        job.value = data;
        data.steps.forEach((step) => {
            steps.value[step.step_id] = step;
        });
    } catch (error) {
        const err = error as Error;
        toast.error(err.message || "Failed to load job details");
    }
};

onMounted(() => {
    getJobOpening();
});

function changeStep(stepKey: string) {
    activeStep.value = stepKey;
    selectedCandidates.value.clear();

    const filtered = filteredCandidates.value;
    const currentCandidateExists = filtered.some((c) => c.applicant_id === activeCandidateId.value);
    if (!currentCandidateExists) {
        activeCandidateId.value = filtered[0]?.applicant_id || null;
    }
}

function selectCandidate(candidateId: string) {
    activeCandidateId.value = candidateId;
}

function toggleCandidateSelection(candidateId: string) {
    if (selectedCandidates.value.has(candidateId)) {
        selectedCandidates.value.delete(candidateId);
    } else {
        selectedCandidates.value.add(candidateId);
    }
    selectedCandidates.value = new Set(selectedCandidates.value);
}

function toggleSelectAll() {
    if (allSelected.value) {
        selectedCandidates.value.clear();
    } else {
        filteredCandidates.value.forEach((c) => selectedCandidates.value.add(c.applicant_id));
    }
    selectedCandidates.value = new Set(selectedCandidates.value);
}

function clearSelection() {
    selectedCandidates.value.clear();
    selectedCandidates.value = new Set();
}

function editJob() {
    showEditDialog.value = true;
}

function showJobDescription() {
    showJobDescriptionDialog.value = true;
}

function editPipeline() {
    if (!job.value) return;
    showEditPipelineDialog.value = true;
}

function onCandidateAdded() {
    toast.success("Candidate added successfully");
    getJobOpening();
}

function onInterviewAssigned(data: { candidateName: string; scheduledOn: string }) {
    toast.success(`Interview assigned to ${data.candidateName} on ${data.scheduledOn}`);
}

function onBulkMoveCompleted(data: { count: number; targetStepLabel: string; targetStepId: string }) {
    toast.success(`${data.count} candidate(s) moved to "${data.targetStepLabel}"`);
    changeStep(data.targetStepId);
    clearSelection();
    getJobOpening();
}

function onEmailSent(data: { recipient: string }) {
    toast.success(`Email sent successfully to ${data.recipient}`);
}

function onPipelineUpdated() {
    toast.success("Pipeline updated successfully");
    getJobOpening();
}
function triggerResumeUpload() {
    if (resumeFileInput.value) {
        resumeFileInput.value.click();
    }
}

async function handleResumeUpload(event: Event) {
    const target = event.target as HTMLInputElement;
    const file = target.files?.[0];
    if (!file) return;

    const validTypes = [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ];
    if (!validTypes.includes(file.type)) {
        toast.error("Please upload a PDF or Word document");
        return;
    }

    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
        toast.error("File size must be less than 10MB");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("is_private", "1");

    try {
        isUploading.value = true;
        uploadProgress.value = 0;

        const response = await fetch("/api/method/upload_file", {
            method: "POST",
            headers: {
                "X-Frappe-CSRF-Token": (window as any).frappe?.csrf_token || "",
            },
            body: formData,
        });

        if (!response.ok) {
            throw new Error("Upload failed");
        }

        const result = await response.json();

        if (result.message && result.message.file_url) {
            uploadProgress.value = 100;
            toast.success("Resume uploaded successfully");
            console.log("File Uploaded:", result.message.file_url);

            await parseResume(result.message.file_url, result.message.name);
        } else {
            throw new Error("Invalid response from server");
        }
    } catch (error) {
        console.error("Upload failed:", error);
        const err = error as Error;
        toast.error(`Upload failed: ${err.message || "Unknown error"}`);
    } finally {
        isUploading.value = false;
        uploadProgress.value = 0;
        if (resumeFileInput.value) {
            resumeFileInput.value.value = "";
        }
    }
}

async function parseResume(fileUrl: string, fileName: string) {
    if (!job.value) return;

    try {
        toast.info("Parsing resume...");

        parsingProfile.value = {
            job_applicant: "Parsing...",
            summary: null,
            skills: null,
            experience: [],
            education: [],
            projects: [],
            links: [],
            personal: {},
        };

        isParsingResume.value = true;
        showProfileDialog.value = true;

        const response = await JobDetailsAPI.parseResume(
            {
                path: `./${import.meta.env.VITE_SITE_NAME}${fileUrl}`,
                file_name: fileName,
                job_opening_id: job.value.name,
                pipeline_step_id: activeStep.value == 'All' ? job.value.steps[1]!.step_id : activeStep.value,
            },
            (progressData: ResumeParseProgressData) => {
                console.log("Resume parsing step:", progressData);

                if (progressData?.data) {
                    if (progressData.data.name) {
                        toast.info(`Parsed ${progressData.data.name} Section`);
                        if (parsingProfile.value) {
                            parsingProfile.value[progressData.data.name as keyof ApplicantParsedProfile] =
                                JSON.parse(progressData.data.content || "{}");
                        }
                    } else {
                        parsingProfile.value = progressData.data as ApplicantParsedProfile;
                    }
                    console.log("parsingProfile:", parsingProfile.value);
                }
            },
        );

        if (response) {
            toast.success("Resume parsed successfully! Candidate added.");
            await getJobOpening();
        }
    } catch (error) {
        console.error("Resume parsing failed:", error);
        const err = error as Error;
        toast.error(`Resume parsing failed: ${err.message || "Unknown error"}`);
        showProfileDialog.value = false;
        parsingProfile.value = null;
    } finally {
        isParsingResume.value = false;
    }
}

async function moveCandidateToStep() {
    if (!activeCandidate.value || !targetStep.value || !job.value) return;

    const currentStepId = activeCandidate.value.applicant_pipeline_step_ref;
    if (targetStep.value === currentStepId) {
        toast.warning("Candidate is already in this stage");
        return;
    }

    const targetStepName =
        job.value.steps.find((s) => s.step_id === targetStep.value)?.step_name || targetStep.value;

    const payload = {
        names: [activeCandidate.value.applicant_id || ""],
        pipeline_step: targetStep.value,
        status: activeCandidate.value.applicant_status || "Open",
    };

    try {
        await JobDetailsAPI.bulkUpdateApplicants(payload);
        toast.success(`${activeCandidate.value.applicant_name} moved to "${targetStepName}"`);

        const candidate = candidates.value.find((c) => c.applicant_id === activeCandidate.value?.applicant_id);
        if (candidate) {
            candidate.applicant_pipeline_step_ref = targetStep.value;
        }
        changeStep(targetStep.value);
    } catch (error) {
        console.log(error);
        const err = error as Error;
        toast.error(err.message || "Failed to move candidate");
    }
}



async function fetchApplicantProfile(applicantId: string) {
    try {
        const profile = await JobDetailsAPI.jobApplicantFind(applicantId, jobId.value) as any;
        console.log(profile);

        return {
            resume: profile.resume || {},
            interviews: profile.interviews || [],
            applicant: profile.applicant || {},
        };
    } catch (error) {
        toast.error("Failed to load profile");
        console.error(error);
        throw error;
    }
}
function shareCandidate() {
    if (!activeCandidate.value) return;

    const shareUrl = `${window.location.origin}${window.location.pathname}?candidate=${activeCandidate.value.applicant_id}`;

    if (navigator.share) {
        navigator
            .share({
                title: `${activeCandidate.value.applicant_name} - Candidate Profile`,
                text: `Check out ${activeCandidate.value.applicant_name}'s profile for ${job.value?.designation}`,
                url: shareUrl,
            })
            .then(() => {
                toast.success("Shared successfully");
            })
            .catch((error) => {
                console.error("Share failed:", error);
                copyToClipboard(shareUrl);
            });
    } else {
        copyToClipboard(shareUrl);
    }
}

function copyToClipboard(text: string) {
    navigator.clipboard
        .writeText(text)
        .then(() => {
            toast.success("Link copied to clipboard");
        })
        .catch((error) => {
            console.error("Copy failed:", error);
            toast.error("Failed to copy link");
        });
}

function printProfile() {
    if (!activeCandidate.value) return;
    toast.info("Print profile feature coming soon...");
}

function copyToJob() {
    if (!activeCandidate.value) return;
    toast.info("Copy to job feature coming soon...");
}

function moveToJob() {
    if (!activeCandidate.value) return;
    toast.info("Move to job feature coming soon...");
}

function editCandidate() {
    if (!activeCandidate.value) return;
    window.open(
        `http://localhost:8001/desk/job-applicant/${activeCandidate.value.applicant_id}`,
        "_blank",
    );
}

async function deleteCandidate() {
    if (!activeCandidate.value) return;

    const confirmed = confirm(
        `Are you sure you want to delete ${activeCandidate.value.applicant_name}? This action cannot be undone.`,
    );

    if (!confirmed) return;

    try {
        toast.info("Delete candidate feature coming soon...");
    } catch (error) {
        console.error(error);
    }
}
</script>