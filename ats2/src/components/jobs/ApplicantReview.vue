<template>
  <div class="applicant-review">
    <div class="text-muted">Review details coming soon...</div>
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
.applicant-review {
  padding: 16px 0;
}
</style>
