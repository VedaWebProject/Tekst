<script setup lang="ts">
import { i18n, setI18nLanguage, I18N_LANGUAGES as LANGS } from '@/i18n';
import { NButton, NDropdown, NIcon } from 'naive-ui';
import type { Size } from 'naive-ui/es/button/src/interface';
import { LanguageOutlined as LangIcon } from '@vicons/material';
import { ref, computed } from 'vue';

export interface Props {
  /**
   * Size of the language switcher component
   */
  size?: Size | undefined;
}
const props = withDefaults(defineProps<Props>(), {
  size: 'medium',
});

const currentLanguage = ref(i18n.global.locale);
const currentLanguageDisplay = computed(() => currentLanguage.value.toUpperCase());

const options = i18n.global.availableLocales.map((l) => {
  const lbl = `${LANGS[l]?.icon ?? l}${LANGS[l] && ' '}${LANGS[l]?.name ?? ''}`;
  return { label: lbl, key: l };
});

function handleLanguageSelect(localeCode: string) {
  localeCode !== currentLanguage.value && setI18nLanguage(localeCode);
}
</script>

<template>
  <n-dropdown trigger="click" :options="options" @select="handleLanguageSelect">
    <n-button id="lang-btn" secondary type="primary" :size="props.size" icon-placement="left">
      <template #icon>
        <n-icon :component="LangIcon" />
      </template>
      {{ currentLanguageDisplay }}
    </n-button>
  </n-dropdown>
</template>
