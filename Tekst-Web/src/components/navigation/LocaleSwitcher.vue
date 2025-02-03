<script setup lang="ts">
import type { LocaleKey } from '@/api';
import { $t } from '@/i18n';
import { useStateStore } from '@/stores';
import { NButton, NIcon, NPopselect } from 'naive-ui';
import { computed } from 'vue';

import { LanguageIcon } from '@/icons';

const state = useStateStore();

const options = computed(() =>
  state.availableLocales.map((lp) => {
    return {
      label: `${lp.icon} ${lp.displayFull}`,
      value: lp.key,
    };
  })
);

function handleLanguageSelect(localeCode: LocaleKey) {
  state.setLocale(localeCode);
}
</script>

<template>
  <n-popselect
    v-if="state.availableLocales.length > 1"
    v-model:value="state.locale"
    trigger="click"
    :options="options"
    @update:value="handleLanguageSelect"
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
  </n-popselect>
</template>
