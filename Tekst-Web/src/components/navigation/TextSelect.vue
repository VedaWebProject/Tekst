<script setup lang="ts">
import type { TextRead } from '@/api';
import TextSelectOption from '@/components/navigation/TextSelectOption.vue';
import TextColorIndicator from '@/components/TextColorIndicator.vue';
import { ExpandArrowDownIcon } from '@/icons';
import { useBrowseStore, useStateStore } from '@/stores';
import { NButton, NDropdown, NFlex, NIcon, useThemeVars } from 'naive-ui';
import { computed, h, ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const state = useStateStore();
const browse = useBrowseStore();
const themeVars = useThemeVars();

const disabled = computed(() => !state.pf?.texts || state.pf.texts.length <= 1);
const dropdownRef = ref();

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
  dropdownRef.value.doUpdateShow(false);
  browse.locationPath = [];

  if (router.currentRoute.value.params.hasOwnProperty('textSlug')) {
    router.push({
      name: router.currentRoute.value.name,
      params: {
        ...router.currentRoute.value.params,
        textSlug: text.slug,
        locId: undefined,
      },
    });
  } else {
    state.text = state.textById(text.id);
  }
}
</script>

<template>
  <n-dropdown
    v-if="state.text"
    ref="dropdownRef"
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
      :title="$t('common.textSelect')"
      class="text-select-btn"
      :style="{ cursor: !disabled ? 'pointer' : 'default' }"
    >
      <n-flex align="center" :wrap="false" style="max-width: 100%">
        <text-color-indicator />
        <span class="text-title ellipsis text-large">{{ state.text.title }}</span>
        <n-icon v-if="!disabled" :component="ExpandArrowDownIcon" style="flex-shrink: 0" />
      </n-flex>
    </n-button>
  </n-dropdown>
</template>

<style scoped>
.text-select-btn {
  max-width: 100%;
  justify-content: flex-start;
}

.text-title {
  line-height: 150%;
  max-width: 100%;
}

.text-subtitle {
  max-width: 100%;
  line-height: 150%;
  padding-bottom: 0.2em;
}

.text-info-btn {
  opacity: 0.6;
}

.text-info-btn:hover {
  opacity: 1;
}
</style>
