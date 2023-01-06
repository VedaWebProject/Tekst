<script setup lang="ts">
import { LANGUAGES as LANGS } from '@/i18n';
import { useSettingsStore } from '@/stores/settings';
import { NButton, NDropdown, NIcon } from 'naive-ui';
import type { Size } from 'naive-ui/es/button/src/interface';
import { LanguageOutlined as LangIcon } from '@vicons/material';

export interface Props {
  /** Size of the language switcher component */
  size?: Size;
}
const props = withDefaults(defineProps<Props>(), {
  size: 'medium',
});

const settings = useSettingsStore();

const options = Object.keys(LANGS).map((l) => {
  const lbl = `${LANGS[l]?.icon ?? l}${LANGS[l] && ' '}${LANGS[l]?.name ?? ''}`;
  return { label: lbl, key: l };
});

function handleLanguageSelect(localeCode: string) {
  localeCode !== settings.language && settings.setLanguage(localeCode);
}
</script>

<template>
  <n-dropdown trigger="click" :options="options" @select="handleLanguageSelect">
    <n-button id="lang-btn" type="primary" :size="props.size" icon-placement="left">
      <template #icon>
        <n-icon :component="LangIcon" />
      </template>
      {{ settings.language.toUpperCase() }}
    </n-button>
  </n-dropdown>
</template>
