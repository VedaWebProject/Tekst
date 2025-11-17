<script setup lang="ts">
import type { TextRead } from '@/api';
import TranslationDisplay from '@/components/generic/TranslationDisplay.vue';
import { NFlex, NIcon } from 'naive-ui';

import { CheckIcon, DisabledVisibleIcon } from '@/icons';
import { useThemeStore } from '@/stores';
import { computed } from 'vue';

const props = defineProps<{
  text: TextRead;
  locale: string;
  selected?: boolean;
}>();

const theme = useThemeStore();
const indicatorStyle = computed(() => ({
  backgroundColor: theme.getTextColors(props.text.id).base,
}));
</script>

<template>
  <n-flex align="stretch" class="text-select-option" :class="{ selected }">
    <div class="text-select-option-indicator" :style="indicatorStyle"></div>
    <div>
      <div>
        {{ text.title }}
      </div>
      <div v-if="text.subtitle?.length" class="text-small translucent">
        <translation-display :value="text.subtitle" />
      </div>
      <div v-if="!text.isActive" class="text-small translucent i">
        <n-icon :component="DisabledVisibleIcon" />
        {{ $t('models.text.isInactive') }}
      </div>
    </div>
    <n-flex v-if="selected" justify="flex-end" align="center" style="flex-grow: 2">
      <n-icon :component="CheckIcon" />
    </n-flex>
  </n-flex>
</template>

<style scoped>
.text-select-option {
  padding: 4px 6px;
  margin: 2px 6px;
  border-radius: 3px;
  cursor: pointer;
  transition: 0.2s;
}

.text-select-option.selected {
  color: var(--primary-color);
}

.text-select-option:hover {
  background-color: #88888825;
}

.text-select-option-indicator {
  width: 12px;
  border-radius: 3px;
}
</style>
