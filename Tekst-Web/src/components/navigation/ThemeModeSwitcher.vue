<script setup lang="ts">
import { $t } from '@/i18n';
import { NButton, NIcon } from 'naive-ui';
import { computed } from 'vue';

import { DarkModeIcon, LightModeIcon } from '@/icons';
import { useThemeStore } from '@/stores';

const theme = useThemeStore();

const icon = computed(() => (theme.dark ? LightModeIcon : DarkModeIcon));
const title = computed(() =>
  theme.dark ? $t('common.switchThemeLight') : $t('common.switchThemeDark')
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
