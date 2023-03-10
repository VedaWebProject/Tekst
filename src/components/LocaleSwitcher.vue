<script setup lang="ts">
import { computed } from 'vue';
import { languageProfiles } from '@/i18n';
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
  Object.keys(languageProfiles).map((l) => {
    const profile = languageProfiles[l];
    return {
      label: `${profile.icon} ${profile.displayFull}`,
      key: l,
      disabled: l === state.language,
    };
  })
);

function handleLanguageSelect(localeCode: string) {
  if (localeCode == state.language) return;

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
      <!-- {{ LANGS[state.language]?.displayShort }} -->
    </n-button>
  </n-dropdown>
</template>
