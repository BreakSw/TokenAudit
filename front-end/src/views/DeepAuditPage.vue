<template>
  <div class="audit-page audit-page--deep" aria-label="深度审计控制台">
    <AuditForm mode="deep" />
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
