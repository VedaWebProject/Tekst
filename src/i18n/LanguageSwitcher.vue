<script setup lang="ts">
import { i18n, setI18nLanguage, I18N_LANGUAGES as LANGS } from '@/i18n';
import { NButton, NDropdown, NIcon } from 'naive-ui';
import { LanguageOutlined as LangIcon } from '@vicons/material';
import { ref } from 'vue';

const selectedLanguage = ref(i18n.global.locale);
const options = i18n.global.availableLocales.map((l) => {
  const lbl = `${LANGS[l]?.icon ?? l}${LANGS[l] && ' '}${LANGS[l]?.name ?? ''}`;
  return { label: lbl, key: l };
});
function handleLanguageSelect(localeCode: string) {
  localeCode !== selectedLanguage.value && setI18nLanguage(localeCode);
}
</script>

<template>
  <n-dropdown trigger="click" :options="options" @select="handleLanguageSelect">
    <n-button id="lang-btn" strong secondary type="primary" size="small" icon-placement="left">
      <template #icon>
        <n-icon :component="LangIcon" />
      </template>
      {{ selectedLanguage.toUpperCase() }}
    </n-button>
  </n-dropdown>
</template>
