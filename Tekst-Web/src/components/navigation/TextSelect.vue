<script setup lang="ts">
import type { TextRead } from '@/api';
import TextSelectOption from '@/components/navigation/TextSelectOption.vue';
import { useBrowseStore, useStateStore } from '@/stores';
import { NButton, NDropdown, NIcon, useThemeVars } from 'naive-ui';
import { computed, h, ref } from 'vue';
import { useRouter } from 'vue-router';

import { ExpandArrowDownIcon } from '@/icons';

const router = useRouter();
const state = useStateStore();
const browse = useBrowseStore();
const themeVars = useThemeVars();

const disabled = computed(() => !state.pf?.texts || state.pf.texts.length <= 1);
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
      locale: state.locale,
      selected: t.id === state.text?.id,
      onClick: () => handleSelect(t),
    });
};

const options = computed(
  () =>
    state.pf?.texts.map((t: TextRead) => ({
      render: renderLabel(t),
      key: t.id,
      type: 'render',
      show: t.id !== state.text?.id,
    })) || []
);

function handleSelect(text: TextRead) {
  if (state.text?.id === text.id) return;
  textSelectDropdownRef.value.doUpdateShow(false);
  browse.locationPath = [];

  router.push({
    name: router.currentRoute.value.params.hasOwnProperty('textSlug')
      ? router.currentRoute.value.name
      : 'browse',
    params: {
      ...router.currentRoute.value.params,
      textSlug: text.slug,
      locId: undefined,
    },
  });

  state.text = state.textById(text.id);
}
</script>

<template>
  <n-dropdown
    v-if="state.text"
    ref="textSelectDropdownRef"
    trigger="click"
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
