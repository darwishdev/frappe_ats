<script setup>
import { ref } from "vue";
const dynamicMessage = ref("Hello from Child.vue");
</script>
<template>
  <div>
	<h3>{{ dynamicMessage }}</h3>
    <h4>Start editing at mawhub/public/js/job_openings/Child.vue</h4>
  </div>
</template>
