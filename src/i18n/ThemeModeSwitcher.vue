<script setup lang="ts">
import { NButton, NIcon } from 'naive-ui';
import type { Size } from 'naive-ui/es/button/src/interface';
import { LightModeOutlined as LightIcon, DarkModeOutlined as DarkIcon } from '@vicons/material';
import { useSettingsStore } from '@/stores/settings';
import { computed } from 'vue';

export interface Props {
  /** Size of the theme mode switcher component */
  size?: Size;
}
const props = withDefaults(defineProps<Props>(), {
  size: 'medium',
});
const settings = useSettingsStore();
const icon = computed(() => (settings.theme === 'dark' ? LightIcon : DarkIcon));
</script>

<template>
  <n-button
    id="lang-btn"
    type="primary"
    :size="props.size"
    icon-placement="left"
    @click="settings.toggleTheme"
  >
    <template #icon>
      <n-icon :component="icon" />
    </template>
  </n-button>
</template>
