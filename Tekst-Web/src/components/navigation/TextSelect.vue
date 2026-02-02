<script setup lang="ts">
import type { TextRead } from '@/api';
import TranslationDisplay from '@/components/generic/TranslationDisplay.vue';
import TextSelectOption from '@/components/navigation/TextSelectOption.vue';
import { useBrowseStore, useStateStore } from '@/stores';
import { NFlex, NSelect, type SelectInst, type SelectOption } from 'naive-ui';
import type { RenderLabel } from 'naive-ui/es/_internal/select-menu/src/interface';
import { computed, h, ref } from 'vue';
import { useRouter } from 'vue-router';

const state = useStateStore();
const router = useRouter();
const browse = useBrowseStore();

const disabled = computed(() => !state.pf?.texts || state.pf.texts.length <= 1);
const selectRef = ref<SelectInst>();

const renderOptionLabel: SelectOption['render'] = (info) => {
  return h(TextSelectOption, {
    text: info.option.text as TextRead,
    locale: state.locale,
    selected: info.selected,
    onClick: () => handleSelect(info.option.text as TextRead),
  });
};

const renderSelectLabel: RenderLabel = (opt: SelectOption & { text: TextRead }, _selected) => {
  return h(TextSelectOption, {
    text: opt.text,
    locale: state.locale,
    singleLine: true,
    onClick: () => handleSelect(opt.text as TextRead),
  });
};

const options = computed<SelectOption[]>(
  () =>
    state.pf?.texts.map((t: TextRead) => ({
      label: t.title,
      value: t.id,
      render: renderOptionLabel,
      text: t,
    })) || []
);

function handleSelect(text: TextRead) {
  if (state.text?.id === text.id) return;
  selectRef.value?.blur();
  browse.locationPath = [];

  if ('textSlug' in router.currentRoute.value.params) {
    router.push({
      name: router.currentRoute.value.name,
      params: {
        ...router.currentRoute.value.params,
        textSlug: text.slug,
        locId: undefined,
      },
    });
  } else {
    state.text = text;
  }
}
</script>

<template>
  <div v-if="!disabled && 'textSlug' in router.currentRoute.value.params" class="text-select">
    <n-flex
      size="large"
      justify="space-between"
      align="center"
      :wrap="false"
      class="text-select-inner"
    >
      <n-select
        ref="selectRef"
        :value="state.text?.id"
        size="large"
        :options="options"
        :render-label="renderSelectLabel"
        :consistent-menu-width="false"
        :style="{
          width: state.vw < 900 ? '100%' : 'unset',
          minWidth: state.vw < 900 ? undefined : '320px',
        }"
        data-tour-key="browseTextSelect"
      />
      <div
        v-if="state.text?.subtitle && state.vw >= 900"
        class="text-large i ellipsis"
        style="color: var(--text-color-translucent)"
      >
        <translation-display :value="state.text?.subtitle" />
      </div>
    </n-flex>
  </div>
</template>

<style scoped>
.text-select {
  background-color: var(--main-bg-color);
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

.text-select-inner {
  padding: var(--gap-md) var(--gap-lg);
  max-width: var(--max-app-width);
  margin: 0 auto;
}

.text-select-inner > * {
  max-width: 100%;
}

.text-select-inner :deep(.n-base-selection-input__content) {
  padding-right: var(--gap-md);
}
</style>
