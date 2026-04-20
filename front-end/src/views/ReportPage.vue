<template>
  <ReportView :audit-id="Number(id)" />
</template>

<script setup>
import ReportView from "../components/ReportView.vue"

const props = defineProps({
  id: { type: String, required: true }
})
</script>
