<script setup lang="ts">
import { NButton, NIcon } from 'naive-ui';
import LightModeOutlined from '@vicons/material/LightModeOutlined';
import DarkModeOutlined from '@vicons/material/DarkModeOutlined';
import { useStateStore } from '@/stores';
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';

const state = useStateStore();
const { t } = useI18n({ useScope: 'global' });

const icon = computed(() => (state.themeMode === 'dark' ? LightModeOutlined : DarkModeOutlined));
const title = computed(() =>
  state.themeMode === 'dark' ? t('general.tipThemeToggleLight') : t('general.tipThemeToggleDark')
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
    @click="state.toggleThemeMode"
  >
    <template #icon>
      <n-icon :component="icon" />
    </template>
  </n-button>
</template>
