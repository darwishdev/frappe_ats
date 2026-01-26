<template>
    <Dialog 
        v-model="isOpen" 
        :options="{ 
            title: 'Parsed Job Description', 
            size: '5xl' 
        }"
    >
        <template #body-content>
            <div class="jdd-content">
                <div v-if="isLoading" class="jdd-loading">
                    <div class="spinner"></div>
                    <p>Parsing job description...</p>
                </div>

                <div v-else-if="Object.keys(parsedData).length > 0" class="jdd-sections">
                    <div v-for="(section, sectionKey) in parsedData" :key="sectionKey">
                        <!-- Special handling for job_opening_details -->
                        <div v-if="sectionKey === 'job_opening_details'" class="jdd-details-card">
                            <h3 class="jdd-details-title">Job Opening Details</h3>
                            
                            <div class="jdd-details-grid">
                                <!-- Job Title -->
                                <div v-if="section.job_title" class="jdd-detail-item jdd-detail-full">
                                    <div class="jdd-detail-icon">
                                        <Briefcase :size="24" />
                                    </div>
                                    <div class="jdd-detail-content">
                                        <div class="jdd-detail-label">Job Title</div>
                                        <div class="jdd-detail-value jdd-detail-highlight">{{ section.job_title }}</div>
                                    </div>
                                </div>

                                <!-- Location -->
                                <div v-if="section.location" class="jdd-detail-item">
                                    <div class="jdd-detail-icon">
                                        <MapPin :size="24" />
                                    </div>
                                    <div class="jdd-detail-content">
                                        <div class="jdd-detail-label">Location</div>
                                        <div class="jdd-detail-value">{{ section.location }}</div>
                                    </div>
                                </div>

                                <!-- Salary Range -->
                                <div v-if="section.lower_range || section.upper_range" class="jdd-detail-item">
                                    <div class="jdd-detail-icon">
                                        <Banknote :size="24" />
                                    </div>
                                    <div class="jdd-detail-content">
                                        <div class="jdd-detail-label">Salary Range</div>
                                        <div class="jdd-detail-value">
                                            {{ formatSalaryRange(section.lower_range, section.upper_range, section.currency) }}
                                        </div>
                                    </div>
                                </div>

                                <!-- Description -->
                                <div v-if="section.description" class="jdd-detail-item jdd-detail-full">
                                    <div class="jdd-detail-icon">
                                        <FileText :size="24" />
                                    </div>
                                    <div class="jdd-detail-content">
                                        <div class="jdd-detail-label">Description</div>
                                        <div class="jdd-detail-value jdd-detail-description">{{ section.description }}</div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Regular section rendering for other keys -->
                        <div v-else class="jdd-section">
                            <!-- Section Title -->
                            <div class="jdd-section-header">
                                <h3 class="jdd-section-title">{{ formatSectionTitle(sectionKey) }}</h3>
                            </div>

                            <!-- Section Description -->
                            <div v-if="section.description" class="jdd-section-description">
                                {{ section.description }}
                            </div>

                            <!-- Bullet Points -->
                            <div v-if="section.bullet_points && section.bullet_points.length > 0" class="jdd-bullet-points">
                                <ul>
                                    <li v-for="(point, idx) in section.bullet_points" :key="idx">
                                        {{ point }}
                                    </li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>

                <div v-else class="jdd-empty">
                    <p>No data parsed yet</p>
                </div>
            </div>
        </template>

        <template #actions>
            <div class="w-full flex justify-between">
                <Button @click="close">
                    Cancel
                </Button>
                <Button 
                    variant="solid" 
                    @click="createJob" 
                    :disabled="isLoading || Object.keys(parsedData).length === 0"
                >
                    Create Job
                </Button>
            </div>
        </template>
    </Dialog>
</template>

<script setup>
import { ref, watch } from 'vue';
import { Dialog, Button } from 'frappe-ui';
import { Briefcase, MapPin, Banknote, FileText } from 'lucide-vue-next';

const props = defineProps({
    modelValue: {
        type: Boolean,
        default: false
    },
    parsedData: {
        type: Object,
        default: () => ({})
    },
    isLoading: {
        type: Boolean,
        default: false
    }
});

const emit = defineEmits(['update:modelValue', 'create']);

const isOpen = ref(props.modelValue);

watch(() => props.modelValue, (newVal) => {
    isOpen.value = newVal;
});

watch(isOpen, (newVal) => {
    emit('update:modelValue', newVal);
});

const close = () => {
    isOpen.value = false;
};

const createJob = () => {
    emit('create', props.parsedData);
    close();
};

const formatSectionTitle = (key) => {
    // Convert camelCase or snake_case to Title Case
    return key
        .replace(/([A-Z])/g, ' $1') // Add space before capitals
        .replace(/_/g, ' ') // Replace underscores with spaces
        .trim()
        .split(' ')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
        .join(' ');
};

const formatSalaryRange = (lower, upper, currency = 'SAR') => {
    const formatNumber = (num) => {
        if (!num) return '';
        return new Intl.NumberFormat('en-US').format(num);
    };

    if (lower && upper) {
        return `${formatNumber(lower)} - ${formatNumber(upper)} ${currency}`;
    } else if (lower) {
        return `From ${formatNumber(lower)} ${currency}`;
    } else if (upper) {
        return `Up to ${formatNumber(upper)} ${currency}`;
    }
    return 'Not specified';
};
</script>

<style scoped>
.jdd-content {
    max-height: 70vh;
    overflow-y: auto;
    padding: 8px;
}

.jdd-loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 300px;
    gap: 16px;
}

.spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #e5e7eb;
    border-top-color: #111827;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

.jdd-loading p {
    color: #6b7280;
    font-size: 14px;
}

.jdd-sections {
    display: flex;
    flex-direction: column;
    gap: 24px;
}

/* Special Job Details Card */
.jdd-details-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 12px;
    padding: 24px;
    color: white;
    box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
}

.jdd-details-title {
    font-size: 20px;
    font-weight: 800;
    margin: 0 0 20px 0;
    color: white;
}

.jdd-details-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
}

.jdd-detail-item {
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 10px;
    padding: 16px;
    display: flex;
    gap: 12px;
    align-items: flex-start;
    transition: all 0.3s ease;
}

.jdd-detail-item:hover {
    background: rgba(255, 255, 255, 0.25);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.jdd-detail-full {
    grid-column: 1 / -1;
}

.jdd-detail-icon {
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
}

.jdd-detail-content {
    flex: 1;
    min-width: 0;
}

.jdd-detail-label {
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    opacity: 0.9;
    margin-bottom: 6px;
}

.jdd-detail-value {
    font-size: 16px;
    font-weight: 600;
    color: white;
    word-break: break-word;
}

.jdd-detail-highlight {
    font-size: 20px;
    font-weight: 800;
}

.jdd-detail-description {
    font-size: 14px;
    font-weight: 400;
    line-height: 1.6;
    white-space: pre-wrap;
}

/* Regular Section Styles */
.jdd-section {
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 16px;
    background: #f9fafb;
}

.jdd-section-header {
    margin-bottom: 12px;
}

.jdd-section-title {
    font-size: 16px;
    font-weight: 700;
    color: #111827;
    margin: 0;
}

.jdd-section-description {
    color: #374151;
    font-size: 14px;
    line-height: 1.6;
    margin-bottom: 12px;
    white-space: pre-wrap;
    word-break: break-word;
}

.jdd-bullet-points {
    margin-top: 12px;
}

.jdd-bullet-points ul {
    margin: 0;
    padding-left: 20px;
    list-style-type: disc;
}

.jdd-bullet-points li {
    color: #374151;
    font-size: 14px;
    line-height: 1.6;
    margin-bottom: 8px;
}

.jdd-bullet-points li:last-child {
    margin-bottom: 0;
}

.jdd-empty {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 200px;
    color: #6b7280;
}
</style>
