<script setup lang="ts">
import { NButton, NIcon } from 'naive-ui';
import LightModeOutlined from '@vicons/material/LightModeOutlined';
import DarkModeOutlined from '@vicons/material/DarkModeOutlined';
import { computed } from 'vue';
import { $t } from '@/i18n';
import { useThemeStore } from '@/stores/theme';

const theme = useThemeStore();

const icon = computed(() => (theme.darkMode ? LightModeOutlined : DarkModeOutlined));
const title = computed(() =>
  theme.darkMode ? $t('general.tipThemeToggleLight') : $t('general.tipThemeToggleDark')
);
</script>

<template>
  <n-button
    secondary
    circle
    size="large"
    icon-placement="left"
    :title="title"
    :focusable="false"
    @click="theme.toggleThemeMode"
  >
    <template #icon>
      <n-icon :component="icon" />
    </template>
  </n-button>
</template>
