<template>
  <el-autocomplete
    class="model-combobox"
    :model-value="modelValue"
    :fetch-suggestions="fetchSuggestions"
    :placeholder="placeholder"
    :disabled="disabled"
    :trigger-on-focus="true"
    :debounce="0"
    value-key="value"
    clearable
    select-when-unmatched
    popper-class="model-combobox-popper"
    @update:model-value="$emit('update:modelValue', $event)"
    @select="selectSuggestion"
    @change="commitValue"
    @keyup.enter="commitValue(modelValue)"
  >
    <template #prefix>
      <span class="model-combobox__prefix" aria-hidden="true">MODEL</span>
    </template>
    <template #default="{ item }">
      <div class="model-suggestion">
        <span class="model-suggestion__value">{{ item.value }}</span>
        <span class="model-suggestion__group">{{ item.group }}</span>
      </div>
    </template>
  </el-autocomplete>
</template>

<script setup>
defineOptions({ name: "ModelCombobox" })

const props = defineProps({
  modelValue: { type: String, default: "" },
  groups: { type: Array, default: () => [] },
  placeholder: { type: String, default: "输入完整模型 ID，或从建议中选择" },
  disabled: { type: Boolean, default: false }
})

const emit = defineEmits(["update:modelValue", "commit"])

function normalizedSuggestions(query) {
  const keyword = String(query || "").trim().toLowerCase()
  const suggestions = props.groups.flatMap((group) =>
    group.options.map((value) => ({ value, group: group.label }))
  )
  if (!keyword) return suggestions

  return suggestions
    .filter((item) => `${item.value} ${item.group}`.toLowerCase().includes(keyword))
    .sort((left, right) => {
      const leftStarts = left.value.toLowerCase().startsWith(keyword)
      const rightStarts = right.value.toLowerCase().startsWith(keyword)
      return Number(rightStarts) - Number(leftStarts)
    })
}

function fetchSuggestions(query, callback) {
  callback(normalizedSuggestions(query))
}

function commitValue(value) {
  emit("commit", String(value ?? props.modelValue ?? ""))
}

function selectSuggestion(item) {
  const value = String(item?.value || "")
  emit("update:modelValue", value)
  emit("commit", value)
}
</script>

<style scoped>
.model-combobox { width: 100%; }
.model-combobox__prefix {
  color: var(--ta-faint);
  font-family: var(--ta-mono);
  font-size: 8px;
  letter-spacing: .08em;
}
</style>

<style>
.model-combobox-popper .el-autocomplete-suggestion__wrap { max-height: 320px; }
.model-combobox-popper .el-autocomplete-suggestion li { min-height: 42px; padding: 6px 10px; line-height: 1.25; }
.model-combobox-popper .el-autocomplete-suggestion li:hover,
.model-combobox-popper .el-autocomplete-suggestion li.highlighted {
  color: var(--ta-green);
  background: rgba(67, 224, 162, .06);
}
.model-suggestion { display: grid; min-width: 0; gap: 3px; }
.model-suggestion__value {
  overflow: hidden;
  color: var(--ta-text);
  font-family: var(--ta-mono);
  font-size: 11px;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.model-suggestion__group {
  overflow: hidden;
  color: var(--ta-faint);
  font-size: 9px;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
