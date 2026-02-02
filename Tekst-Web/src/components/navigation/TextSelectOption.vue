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
  singleLine?: boolean;
}>();

const theme = useThemeStore();
const indicatorStyle = computed(() => ({
  backgroundColor: theme.getTextColors(props.text.id).base,
}));
</script>

<template>
  <n-flex
    :align="singleLine ? 'center' : 'stretch'"
    class="opt"
    :class="{ selected, 'menu-opt': !singleLine }"
    :wrap="false"
  >
    <div
      class="opt-indicator"
      :class="{ 'opt-indicator-single-line': singleLine }"
      :style="indicatorStyle"
    ></div>
    <div>
      <div class="ellipsis">
        {{ text.title }}
      </div>
      <div v-if="text.subtitle?.length && !singleLine" class="text-small translucent">
        <translation-display :value="text.subtitle" />
      </div>
      <div v-if="!text.isActive && !singleLine" class="text-small translucent i">
        <n-icon :component="DisabledVisibleIcon" />
        {{ $t('models.text.isInactive') }}
      </div>
    </div>
    <n-flex v-if="selected && !singleLine" justify="flex-end" align="center" style="flex-grow: 2">
      <n-icon :component="CheckIcon" />
    </n-flex>
  </n-flex>
</template>

<style scoped>
.opt {
  border-radius: 3px;
  cursor: pointer;
  transition: 0.2s;
}

.opt.selected {
  color: var(--primary-color);
}

.menu-opt {
  padding: 4px 6px;
  margin: 2px 6px;
}

.menu-opt:hover {
  background-color: #88888825;
}

.opt-indicator {
  width: 12px;
  border-radius: 3px;
}

.opt-indicator-single-line {
  width: 16px;
  height: 16px;
  border-radius: 50%;
}
</style>
