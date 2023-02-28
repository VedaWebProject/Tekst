<script setup lang="ts">
import { NButton, NIcon } from 'naive-ui';
import LightModeOutlined from '@vicons/material/LightModeOutlined';
import DarkModeOutlined from '@vicons/material/DarkModeOutlined';
import { useSettingsStore } from '@/stores';
import { computed } from 'vue';
import { i18n } from '@/i18n';

const settings = useSettingsStore();
const t = i18n.global.t;

const icon = computed(() => (settings.theme === 'dark' ? LightModeOutlined : DarkModeOutlined));
const title = computed(() =>
  settings.theme === 'dark' ? t('general.tipThemeToggleLight') : t('general.tipThemeToggleDark')
);
</script>

<template>
  <n-button
    secondary
    circle
    size="large"
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
