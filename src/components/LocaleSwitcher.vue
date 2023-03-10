<script setup lang="ts">
import { computed } from 'vue';
import { localeProfiles } from '@/i18n';
import { useMessagesStore, useStateStore } from '@/stores';
import { NButton, NDropdown, NIcon } from 'naive-ui';
import LanguageOutlined from '@vicons/material/LanguageOutlined';
import { useI18n } from 'vue-i18n';

const props = defineProps<{
  dropdownSize?: 'small' | 'medium' | 'large' | 'huge' | undefined;
}>();

const state = useStateStore();
const messages = useMessagesStore();
const { t } = useI18n({ useScope: 'global' });

const options = computed(() =>
  Object.keys(localeProfiles).map((l) => {
    const profile = localeProfiles[l];
    return {
      label: `${profile.icon} ${profile.displayFull}`,
      key: l,
      disabled: l === state.locale,
    };
  })
);

function handleLanguageSelect(localeCode: string) {
  if (localeCode == state.locale) return;

  state.setLanguage(localeCode).catch((e) => {
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
      <!-- {{ LANGS[state.locale]?.displayShort }} -->
    </n-button>
  </n-dropdown>
</template>
