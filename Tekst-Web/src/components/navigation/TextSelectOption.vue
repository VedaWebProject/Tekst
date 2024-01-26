<script setup lang="ts">
import type { TextRead } from '@/api';
import { NIcon } from 'naive-ui';
import TranslationDisplay from '@/components/generic/TranslationDisplay.vue';

import { DisabledVisibleIcon } from '@/icons';

defineProps<{
  text: TextRead;
  locale: string;
  selected?: boolean;
}>();
</script>

<template>
  <div class="text-select-option">
    <div class="text-select-option-indicator" :style="{ backgroundColor: text.accentColor }"></div>
    <div>
      <div>
        {{ text.title }}
      </div>
      <div
        v-if="text.subtitle?.length"
        style="font-size: var(--app-ui-font-size-tiny); opacity: 0.8"
      >
        <TranslationDisplay :value="text.subtitle" />
      </div>
      <div
        v-if="!text.isActive"
        style="font-size: var(--app-ui-font-size-small); font-style: italic; opacity: 0.5"
      >
        <n-icon :component="DisabledVisibleIcon" />
        {{ $t('models.text.isInactive') }}
      </div>
    </div>
  </div>
</template>

<style scoped>
.text-select-option {
  display: flex;
  align-items: stretch;
  gap: 12px;
  padding: 4px 6px;
  margin: 2px 6px;
  border-radius: 3px;
  cursor: pointer;
  transition: 0.2s;
}

.text-select-option:hover {
  background-color: #88888825;
}

.text-select-option-indicator {
  width: 12px;
  border-radius: 3px;
}
</style>
