<script setup lang="ts">
import type { TextRead } from '@/api';
import { computed, h, ref } from 'vue';
import { useBrowseStore, useStateStore } from '@/stores';
import { useRouter } from 'vue-router';
import { NDropdown, NButton, NIcon, useThemeVars } from 'naive-ui';
import TextSelectOption from '@/components/navigation/TextSelectOption.vue';
import { usePlatformData } from '@/composables/platformData';
import { useI18n } from 'vue-i18n';

import { ExpandArrowDownIcon } from '@/icons';

const router = useRouter();
const state = useStateStore();
const browse = useBrowseStore();
const themeVars = useThemeVars();
const { locale } = useI18n();
const { pfData } = usePlatformData();

const disabled = computed(() => !pfData.value?.texts || pfData.value.texts.length <= 1);
const textSelectDropdownRef = ref();

const btnStyle = computed(() => ({
  fontSize: 'inherit',
  fontWeight: 'var(--font-weight-bold)',
  cursor: !disabled.value ? 'pointer' : 'default',
  maxWidth: '100%',
}));

const renderLabel = (t: TextRead) => {
  return () =>
    h(TextSelectOption, {
      text: t,
      locale: locale.value,
      selected: t.id === state.text?.id,
      onClick: () => handleSelect(t),
    });
};

const options = computed(
  () =>
    pfData.value?.texts.map((t: TextRead) => ({
      render: renderLabel(t),
      key: t.id,
      type: 'render',
      show: t.id !== state.text?.id,
    })) || []
);

function handleSelect(text: TextRead) {
  textSelectDropdownRef.value.doUpdateShow(false);
  browse.locationPath = [];

  if ('text' in router.currentRoute.value.params) {
    router.push({
      name: router.currentRoute.value.name || 'browse',
      params: { ...router.currentRoute.value.params, text: text.slug },
    });
  }

  state.text = pfData.value?.texts.find((t) => t.id === text.id);
}
</script>

<template>
  <n-dropdown
    v-if="state.text"
    ref="textSelectDropdownRef"
    trigger="click"
    to="#app-container"
    :options="options"
    :disabled="disabled"
    placement="bottom-start"
  >
    <n-button
      text
      icon-placement="right"
      :color="themeVars.baseColor"
      :focusable="false"
      :keyboard="false"
      :title="$t('general.textSelect')"
      :style="btnStyle"
    >
      <template v-if="!disabled" #icon>
        <n-icon :component="ExpandArrowDownIcon" />
      </template>
      <div class="text-select-label">
        {{ state.text.title }}
      </div>
    </n-button>
  </n-dropdown>
</template>

<style scoped>
.text-select-label {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 200%;
}
</style>
