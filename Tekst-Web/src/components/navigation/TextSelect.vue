<script setup lang="ts">
import type { TextRead } from '@/api';
import TextSelectOption from '@/components/navigation/TextSelectOption.vue';
import { ExpandArrowDownIcon } from '@/icons';
import { useBrowseStore, useStateStore } from '@/stores';
import { NButton, NDropdown, NIcon, useThemeVars } from 'naive-ui';
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
    ref="dropdownRef"
    trigger="click"
    :options="options"
    :disabled="disabled"
    placement="bottom-start"
  >
    <n-button
      ghost
      :color="themeVars.baseColor"
      icon-placement="right"
      :focusable="false"
      :keyboard="false"
      :title="$t('common.textSelect')"
      class="text-select-btn"
      :style="{ cursor: !disabled ? 'pointer' : 'default' }"
    >
      <template v-if="!disabled" #icon>
        <n-icon :component="ExpandArrowDownIcon" />
      </template>
      <div class="text-title ellipsis text-large">{{ state.text?.title || '???' }}</div>
    </n-button>
  </n-dropdown>
</template>

<style scoped>
.text-select-btn {
  max-width: 100%;
  justify-content: flex-start;
}

.text-select-btn.n-button--ghost:hover {
  background-color: #ffffff1a;
}

.n-button :deep(.n-button__border) {
  border: 1px solid var(--base-color-translucent);
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
