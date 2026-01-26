<template>
  <div class="applicant-files">
    <div class="text-muted">Files coming soon...</div>
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
.applicant-files {
  padding: 16px 0;
}
</style>
