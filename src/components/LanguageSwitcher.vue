<script setup lang="ts">
import { LANGUAGES as LANGS } from '@/i18n';
import { useSettingsStore, useMessagesStore } from '@/stores';
import { NButton, NDropdown, NIcon } from 'naive-ui';
import LanguageOutlined from '@vicons/material/LanguageOutlined';
import { i18n } from '@/i18n';

const props = defineProps<{
  dropdownSize?: 'small' | 'medium' | 'large' | 'huge' | undefined;
}>();

const settings = useSettingsStore();
const messages = useMessagesStore();
const t = i18n.global.t;

const options = Object.keys(LANGS).map((l) => {
  return {
    label: `${LANGS[l]?.icon ?? l}${LANGS[l] && ' '}${LANGS[l]?.displayFull ?? ''}`,
    key: l,
  };
});

function handleLanguageSelect(localeCode: string) {
  if (localeCode == settings.language) return;

  settings.setLanguage(localeCode).catch((e) => {
    messages.warning(t('errors.serverI18n'));
    console.error(e);
  });
}
</script>

<template>
  <n-dropdown
    trigger="click"
    :options="options"
    :size="props.dropdownSize"
    @select="handleLanguageSelect"
  >
    <n-button
      secondary
      circle
      size="large"
      icon-placement="left"
      :title="$t('i18n.tipSwitcher')"
      :focusable="false"
    >
      <template #icon>
        <n-icon :component="LanguageOutlined" />
      </template>
      <!-- {{ LANGS[settings.language]?.displayShort }} -->
    </n-button>
  </n-dropdown>
</template>
