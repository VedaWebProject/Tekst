<script setup lang="ts">
import { LANGUAGES as LANGS } from '@/i18n';
import { useSettingsStore, useMessagesStore } from '@/stores';
import { NButton, NDropdown, NIcon } from 'naive-ui';
import type { Size } from 'naive-ui/es/button/src/interface';
import LanguageOutlined from '@vicons/material/LanguageOutlined';
import { i18n } from '@/i18n';

export interface Props {
  /** Size of the language switcher component */
  size?: Size;
}
const props = withDefaults(defineProps<Props>(), {
  size: 'medium',
});

const settings = useSettingsStore();
const messages = useMessagesStore();

const options = Object.keys(LANGS).map((l) => {
  return {
    label: `${LANGS[l]?.icon ?? l}${LANGS[l] && ' '}${LANGS[l]?.displayFull ?? ''}`,
    key: l,
  };
});

function handleLanguageSelect(localeCode: string) {
  if (localeCode == settings.language) return;

  settings.setLanguage(localeCode).catch((e) => {
    messages.create({
      text: i18n.global.t('errors.serverI18n'),
      type: 'warning',
    });
    console.error(e);
  });
}
</script>

<template>
  <n-dropdown trigger="click" :options="options" @select="handleLanguageSelect">
    <n-button
      id="lang-btn"
      type="default"
      :size="props.size"
      icon-placement="left"
      :title="$t('i18n.tipSwitcher')"
    >
      <template #icon>
        <n-icon :component="LanguageOutlined" />
      </template>
      {{ LANGS[settings.language]?.displayShort }}
    </n-button>
  </n-dropdown>
</template>
