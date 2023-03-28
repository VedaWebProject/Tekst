<script setup lang="ts">
import { computed } from 'vue';
import { NSwitch, NIcon } from 'naive-ui';
import CheckRound from '@vicons/material/CheckRound';

const props = defineProps<{
  active: boolean;
  title: string;
  layerType: string;
}>();
const emits = defineEmits<{ (e: 'update:active', active: boolean): void }>();

const active = computed({
  get() {
    return props.active;
  },
  set(value: boolean) {
    emits('update:active', value);
  },
});
</script>

<template>
  <div class="layer-toggle-item">
    <n-switch v-model:value="active" size="large">
      <template #checked-icon>
        <n-icon :component="CheckRound" />
      </template>
    </n-switch>
    <div style="min-width: 1px">
      <div class="layer-toggle-item-title">{{ props.title }}</div>
      <div class="layer-toggle-item-type">{{ props.layerType }}</div>
    </div>
  </div>
</template>

<style scoped>
.layer-toggle-item {
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  gap: 24px;
  margin-bottom: 1rem;
}

.layer-toggle-item .layer-toggle-item-title {
  color: var(--accent-color);
  font-size: var(--app-ui-font-size-medium);
  font-weight: var(--app-ui-font-weight-normal);
}

.layer-toggle-item .layer-toggle-item-type {
  opacity: 0.6;
  font-size: var(--app-ui-font-size-mini);
  font-weight: var(--app-ui-font-weight-light);
}

.layer-toggle-item .layer-toggle-item-title,
.layer-toggle-item .layer-toggle-item-type {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
