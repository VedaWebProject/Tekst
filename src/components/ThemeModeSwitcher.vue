<script setup lang="ts">
import { NButton, NIcon } from 'naive-ui';
import type { Size } from 'naive-ui/es/button/src/interface';
import LightModeOutlined from '@vicons/material/LightModeOutlined';
import DarkModeOutlined from '@vicons/material/DarkModeOutlined';
import { useSettingsStore } from '@/stores';
import { computed } from 'vue';
import { i18n } from '@/i18n';

export interface Props {
  /** Size of the theme mode switcher component */
  size?: Size;
}
const props = withDefaults(defineProps<Props>(), {
  size: 'medium',
});

const settings = useSettingsStore();
const t = i18n.global.t;

const icon = computed(() => (settings.theme === 'dark' ? LightModeOutlined : DarkModeOutlined));
const title = computed(() =>
  settings.theme === 'dark' ? t('general.tipThemeToggleLight') : t('general.tipThemeToggleDark')
);
</script>

<template>
  <n-button
    id="lang-btn"
    quaternary
    circle
    :size="props.size"
    icon-placement="left"
    @click="settings.toggleTheme"
    :title="title"
    :focusable="false"
  >
    <template #icon>
      <n-icon :component="icon" />
    </template>
  </n-button>
</template>
