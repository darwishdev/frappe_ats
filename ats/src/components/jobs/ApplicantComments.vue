<template>
  <div class="applicant-comments">
    <div class="text-muted">Comments coming soon...</div>
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
.applicant-comments {
  padding: 16px 0;
}
</style>
