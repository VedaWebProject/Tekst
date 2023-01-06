<script setup lang="ts">
import { i18n, setI18nLanguage, I18N_LANGUAGES as LANGS } from '@/i18n';
import { NButton, NDropdown, NIcon } from 'naive-ui';
import { LanguageOutlined as LangIcon } from '@vicons/material';
import { ref } from 'vue';

const selectedLanguage = ref(i18n.global.locale);
const options = i18n.global.availableLocales.map((l) => {
  const optLabel = `${LANGS[l].icon} ${LANGS[l].name}`;
  return { label: optLabel, key: l };
});
</script>

<template>
  <n-dropdown trigger="click" :options="options" @select="setI18nLanguage">
    <n-button strong secondary type="primary" size="small" icon-placement="left">
      <template #icon>
        <n-icon :component="LangIcon" />
      </template>
      {{ selectedLanguage.toUpperCase() }}
    </n-button>
  </n-dropdown>
</template>

<style scoped></style>
