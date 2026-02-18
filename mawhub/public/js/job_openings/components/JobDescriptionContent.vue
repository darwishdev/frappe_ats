<script setup>
import { computed } from 'vue';

const props = defineProps({
  parsedData: {
    type: Object,
    default: () => ({})
  },
  jobDetails: {
    type: Object,
    default: null
  }
});

const formatSectionTitle = (key) => {
  return key
    .replace(/([A-Z])/g, ' $1')
    .replace(/_/g, ' ')
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

const parsedDataObject = computed(() => {
  if (!props.parsedData || typeof props.parsedData !== 'object') return {};
  return props.parsedData;
});
</script>

<template>
  <div class="jdd-content">
    <div
      v-if="Object.keys(parsedDataObject).length > 0"
      class="jdd-sections"
    >
      <!-- Job Details Card from props -->
      <div
        v-if="jobDetails"
        class="jdd-details-card"
      >
        <h3 class="jdd-details-title">
          Job Details
        </h3>
                        
        <div class="jdd-details-grid">
          <!-- Job Title -->
          <div class="jdd-detail-item jdd-detail-full">
            <div class="jdd-detail-icon">
              <span class="fa fa-briefcase" style="font-size: 20px;"></span>
            </div>
            <div class="jdd-detail-content">
              <div class="jdd-detail-label">
                Job Title
              </div>
              <div class="jdd-detail-value jdd-detail-highlight">
                {{ jobDetails.designation || jobDetails.title }}
              </div>
            </div>
          </div>

          <!-- Department -->
          <div v-if="jobDetails.department" class="jdd-detail-item">
            <div class="jdd-detail-icon">
              <span class="fa fa-users" style="font-size: 20px;"></span>
            </div>
            <div class="jdd-detail-content">
              <div class="jdd-detail-label">
                Department
              </div>
              <div class="jdd-detail-value">
                {{ jobDetails.department }}
              </div>
            </div>
          </div>

          <!-- Location -->
          <div v-if="jobDetails.location" class="jdd-detail-item">
            <div class="jdd-detail-icon">
              <span class="fa fa-map-marker" style="font-size: 20px;"></span>
            </div>
            <div class="jdd-detail-content">
              <div class="jdd-detail-label">
                Location
              </div>
              <div class="jdd-detail-value">
                {{ jobDetails.location }}
              </div>
            </div>
          </div>

          <!-- Work Mode -->
          <div v-if="jobDetails.work_mode" class="jdd-detail-item">
            <div class="jdd-detail-icon">
              <span class="fa fa-briefcase" style="font-size: 20px;"></span>
            </div>
            <div class="jdd-detail-content">
              <div class="jdd-detail-label">
                Work Mode
              </div>
              <div class="jdd-detail-value">
                {{ jobDetails.work_mode }}
              </div>
            </div>
          </div>

          <!-- Pipeline -->
          <div v-if="jobDetails.pipeline_name" class="jdd-detail-item">
            <div class="jdd-detail-icon">
              <span class="fa fa-file-text-o" style="font-size: 20px;"></span>
            </div>
            <div class="jdd-detail-content">
              <div class="jdd-detail-label">
                Pipeline
              </div>
              <div class="jdd-detail-value">
                {{ jobDetails.pipeline_name }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div
        v-for="(section, sectionKey) in parsedDataObject"
        :key="sectionKey"
      >
        <!-- Special handling for job_opening_details -->
        <div
          v-if="sectionKey === 'job_opening_details'"
          class="jdd-details-card"
        >
          <h3 class="jdd-details-title">
            Job Opening
          </h3>
                            
          <div class="jdd-details-grid">
            <!-- Job Title -->
            <div
              v-if="section.job_title"
              class="jdd-detail-item jdd-detail-full"
            >
              <div class="jdd-detail-icon">
                <span class="fa fa-briefcase" style="font-size: 20px;"></span>
              </div>
              <div class="jdd-detail-content">
                <div class="jdd-detail-label">
                  Job Title
                </div>
                <div class="jdd-detail-value">
                  {{ section.job_title }}
                </div>
              </div>
            </div>

            <!-- Location -->
            <div class="jdd-detail-item">
              <div class="jdd-detail-icon">
                <span class="fa fa-map-marker" style="font-size: 20px;"></span>
              </div>
              <div class="jdd-detail-content">
                <div class="jdd-detail-label">
                  Location
                </div>
                <div class="jdd-detail-value">
                  {{ section.location || 'N/A' }}
                </div>
              </div>
            </div>

            <!-- Salary Range -->
            <div class="jdd-detail-item">
              <div class="jdd-detail-icon">
                <span class="fa fa-money" style="font-size: 20px;"></span>
              </div>
              <div class="jdd-detail-content">
                <div class="jdd-detail-label">
                  Salary Range
                </div>
                <div class="jdd-detail-value">
                  {{ formatSalaryRange(section.lower_range, section.upper_range, section.currency) || 'N/A' }}
                </div>
              </div>
            </div>

            <!-- Description -->
            <div class="jdd-detail-item jdd-detail-full">
              <div class="jdd-detail-icon">
                <span class="fa fa-file-text-o" style="font-size: 20px;"></span>
              </div>
              <div class="jdd-detail-content">
                <div class="jdd-detail-label">
                  Description
                </div>
                <div class="jdd-detail-value jdd-detail-description">
                  {{ section.description || 'N/A' }}
                </div>
              </div>
            </div>
          </div>

          <!-- Footer -->
          <div
            v-if="section.footer"
            class="jdd-details-footer"
          >
            {{ section.footer }}
          </div>
        </div>

        <!-- Regular section rendering for other keys -->
        <div
          v-else
          class="jdd-section"
        >
          <!-- Section Title -->
          <div class="jdd-section-header">
            <h3 class="jdd-section-title">
              {{ formatSectionTitle(sectionKey) }}
            </h3>
          </div>

          <!-- Section Description -->
          <div
            v-if="section.description"
            class="jdd-section-description"
          >
            {{ section.description }}
          </div>

          <!-- Bullet Points -->
          <div
            v-if="section.bullet_points && section.bullet_points.length > 0"
            class="jdd-bullet-points"
          >
            <ul :class="{ 'jdd-numbered-list': section.is_number_list }">
              <li
                v-for="(point, idx) in section.bullet_points"
                :key="idx"
              >
                {{ point }}
              </li>
            </ul>
          </div>

          <!-- Footer -->
          <div
            v-if="section.footer"
            class="jdd-section-footer"
          >
            {{ section.footer }}
          </div>
        </div>
      </div>
    </div>

    <div
      v-else
      class="jdd-empty"
    >
      <p>No parsed job description available</p>
    </div>
  </div>
</template>

<style scoped>
.jdd-content {
  max-height: 70vh;
  overflow-y: auto;
  padding: 8px;
}

.jdd-sections {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Special Job Details Card */
.jdd-details-card {
  position: relative;
  background: #fdfefe;
  border: 1px solid #e2e8f0;
  border-radius: 14px;
  padding: 22px;
  color: #0f172a;
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
  overflow: hidden;
}

.jdd-details-card::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(120deg, rgba(59, 130, 246, 0.12), #7700bc0b);
  opacity: 0.7;
  pointer-events: none;
}

.jdd-details-title {
  position: relative;
  font-size: 18px;
  margin: 0 0 16px 0;
  color: #0f172a;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 6px 12px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.8);
  box-shadow: 0 6px 12px rgba(15, 23, 42, 0.05);
}

.jdd-details-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.jdd-detail-item {
  position: relative;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 14px 16px;
  display: flex;
  gap: 12px;
  align-items: flex-start;
  transition: box-shadow 0.2s ease, transform 0.2s ease, border-color 0.2s ease;
  box-shadow: 0 4px 10px rgba(15, 23, 42, 0.04);
}

.jdd-detail-item:hover {
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.08);
  transform: translateY(-2px);
  border-color: #cbd5e1;
}

.jdd-detail-full {
  grid-column: 1 / -1;
}

.jdd-detail-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(145deg, #e2e8f0, #f8fafc);
  color: #0f172a;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.6);
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
  color: #52627a;
  margin-bottom: 6px;
}

.jdd-detail-value {
  font-size: 15.5px;
  color: #0f172a;
  word-break: break-word;
}

.jdd-detail-highlight {
  font-size: 18px;
  font-weight: 800;
}

.jdd-detail-description {
  font-size: 14px;
  font-weight: 400;
  line-height: 1.6;
  color: #1e293b;
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

.jdd-bullet-points ul.jdd-numbered-list {
  list-style-type: decimal;
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

.jdd-section-footer {
  color: #4b5563;
  font-size: 13px;
  line-height: 1.6;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #e5e7eb;
  font-style: italic;
  white-space: pre-wrap;
  word-break: break-word;
}

.jdd-details-footer {
  position: relative;
  color: #475569;
  font-size: 13px;
  line-height: 1.6;
  margin-top: 16px;
  padding: 12px 16px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid #e2e8f0;
  font-style: italic;
  white-space: pre-wrap;
  word-break: break-word;
}

.jdd-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  color: #6b7280;
}

/* Dark mode support */
[data-theme="dark"] .jdd-details-card {
  background: #2a2a2a;
  border-color: #3a3a3a;
  color: #f0f0f0;
}

[data-theme="dark"] .jdd-details-card::before {
  background: linear-gradient(120deg, rgba(59, 130, 246, 0.08), rgba(119, 0, 188, 0.05));
}

[data-theme="dark"] .jdd-details-title {
  color: #f0f0f0;
  background: rgba(42, 42, 42, 0.8);
}

[data-theme="dark"] .jdd-detail-item {
  background: rgba(51, 51, 51, 0.9);
  border-color: #3a3a3a;
}

[data-theme="dark"] .jdd-detail-icon {
  background: linear-gradient(145deg, #3a3a3a, #2a2a2a);
  color: #e0e0e0;
}

[data-theme="dark"] .jdd-detail-label {
  color: #a0a0a0;
}

[data-theme="dark"] .jdd-detail-value {
  color: #e0e0e0;
}

[data-theme="dark"] .jdd-section {
  background: #2a2a2a;
  border-color: #3a3a3a;
}

[data-theme="dark"] .jdd-section-title {
  color: #f0f0f0;
}

[data-theme="dark"] .jdd-section-description,
[data-theme="dark"] .jdd-bullet-points li {
  color: #d0d0d0;
}

[data-theme="dark"] .jdd-section-footer {
  color: #a0a0a0;
  border-top-color: #3a3a3a;
}

[data-theme="dark"] .jdd-details-footer {
  color: #a0a0a0;
  background: rgba(42, 42, 42, 0.7);
  border-color: #3a3a3a;
}

[data-theme="dark"] .jdd-empty {
  color: #a0a0a0;
}
</style>
