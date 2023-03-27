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
    <div class="layer-toggle-item-info">{{ props.title }} ({{ props.layerType }})</div>
  </div>
</template>

<style scoped>
.layer-toggle-item {
  display: flex;
  align-items: center;
  gap: 12px;
}
</style>
