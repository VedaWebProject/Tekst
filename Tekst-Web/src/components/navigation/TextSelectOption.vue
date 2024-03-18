<script setup lang="ts">
import type { TextRead } from '@/api';
import { NIcon } from 'naive-ui';
import TranslationDisplay from '@/components/generic/TranslationDisplay.vue';

import { DisabledVisibleIcon } from '@/icons';
import { computed } from 'vue';
import { useThemeStore } from '@/stores';

const props = defineProps<{
  text: TextRead;
  locale: string;
  selected?: boolean;
}>();

const theme = useThemeStore();
const indicatorStyle = computed(() => ({
  backgroundColor: theme.generateAccentColorVariants(props.text.accentColor).base,
}));
</script>

<template>
  <div class="text-select-option">
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
