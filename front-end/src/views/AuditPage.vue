<template>
  <div class="audit-page" aria-label="快速审计控制台">
    <AuditForm mode="quick" />
  </div>
</template>

<script setup>
import AuditForm from "../components/AuditForm.vue"
</script>

<style scoped>
.audit-page {
  width: 100%;
}
</style>
