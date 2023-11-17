<script setup lang="ts">
import type { TextRead } from '@/api';
import { NIcon } from 'naive-ui';
import DisabledVisibleRound from '@vicons/material/DisabledVisibleRound';
import { computed } from 'vue';
import { determineTextSubtitle } from '@/utils';

const props = defineProps<{
  text: TextRead;
  locale: string;
  selected?: boolean;
}>();

const subtitle = computed(() => determineTextSubtitle(props.text.subtitle || [], props.locale));
</script>

<template>
  <div class="text-select-option" :title="subtitle">
    <div class="text-select-option-indicator" :style="{ backgroundColor: text.accentColor }"></div>
    <div>
      <div>
        {{ text.title }}
      </div>
      <div style="font-size: var(--app-ui-font-size-tiny); opacity: 0.8">
        {{ subtitle }}
      </div>
      <div
        v-if="!text.isActive"
        style="font-size: var(--app-ui-font-size-small); font-style: italic; opacity: 0.5"
      >
        <n-icon :component="DisabledVisibleRound" />
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
}

.text-select-option:hover {
  background-color: #88888825;
}

.text-select-option-indicator {
  width: 12px;
  border-radius: 3px;
}
</style>
