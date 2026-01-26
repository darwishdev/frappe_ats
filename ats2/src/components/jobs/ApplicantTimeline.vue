<template>
  <div class="applicant-timeline">
    <div class="empty-state">
      <div class="empty-state-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 8v4l3 3m6-3a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"/>
        </svg>
      </div>
      <h3 class="empty-state-title">No Timeline Yet</h3>
      <p class="empty-state-description">
        Timeline events and activity history will appear here once actions are taken on this applicant.
      </p>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  candidate: {
    type: Object,
    default: null,
  },
});
</script>

<style scoped>
.applicant-timeline {
  padding: 16px 0;
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-state {
  text-align: center;
  max-width: 400px;
  padding: 48px 24px;
}

.empty-state-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 96px;
  height: 96px;
  margin: 0 auto 24px;
  background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
  border-radius: 50%;
  color: #9ca3af;
}

.empty-state-title {
  font-size: 20px;
  font-weight: 700;
  color: #111827;
  margin: 0 0 12px 0;
}

.empty-state-description {
  font-size: 15px;
  line-height: 1.6;
  color: #6b7280;
  margin: 0;
}
</style>
