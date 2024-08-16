<script setup lang="ts">
import { computed } from 'vue';
import { useStateStore } from '@/stores';
import { NButton, NDropdown, NIcon } from 'naive-ui';
import { $t } from '@/i18n';
import type { LocaleKey } from '@/api';

import { LanguageIcon } from '@/icons';

const state = useStateStore();

const options = computed(() =>
  state.availableLocales.map((lp) => {
    return {
      label: `${lp.icon} ${lp.displayFull}`,
      key: lp.key,
      disabled: lp.key === state.locale,
    };
  })
);

function handleLanguageSelect(localeCode: LocaleKey) {
  if (localeCode !== state.locale) {
    state.setLocale(localeCode);
  }
}
</script>

<template>
  <n-dropdown
    v-if="state.availableLocales.length > 1"
    trigger="click"
    to="#app-container"
    :options="options"
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
        <n-icon :component="LanguageIcon" />
      </template>
    </n-button>
  </n-dropdown>
</template>
