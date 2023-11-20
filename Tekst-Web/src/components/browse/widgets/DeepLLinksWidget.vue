<script setup lang="ts">
import UnitContainerHeaderWidget from '@/components/browse/UnitContainerHeaderWidget.vue';
import TranslateRound from '@vicons/material/TranslateRound';
import type { DeepLLinksConfig } from '@/api';
import { computed, h } from 'vue';
import type { VNodeChild } from 'vue';
import { useStateStore } from '@/stores';
import { NDropdown } from 'naive-ui';
import type { DropdownOption } from 'naive-ui';

const DEEPL_TRANSLATOR_URL = 'https://www.deepl.com/translator';

const props = defineProps<{
  widgetConfig: DeepLLinksConfig;
  layer: Record<string, any>;
}>();

const state = useStateStore();

const unitsTextEncoded = computed<string>(() => {
  const unitsText = props.layer.units
    .map((u: Record<string, any>) => u.text as string)
    .join('\n')
    .trim();
  return encodeURIComponent(
    unitsText
      .replace(/[^\p{L}\-.?!"\n']+/gu, ' ')
      .replace(/ ?\n ?/g, '\n')
      .trim()
  );
});

const options = computed(
  () =>
    props.widgetConfig?.languages?.map((l) => ({
      label: l,
      key: l,
    }))
);

function renderOption(option: DropdownOption) {
  return h(
    'a',
    {
      href: `${DEEPL_TRANSLATOR_URL}#${props.widgetConfig.sourceLanguage}/${option.key}/${unitsTextEncoded.value}`,
      target: '_blank',
    },
    {
      default: () => option.label as VNodeChild,
    }
  );
}
</script>

<template>
  <n-dropdown
    v-if="props.widgetConfig?.enabled && unitsTextEncoded && props.widgetConfig"
    trigger="click"
    :options="options"
    to="#app-container"
    placement="bottom-start"
    :size="state.dropdownSize"
    :render-label="renderOption"
    show-arrow
  >
    <UnitContainerHeaderWidget
      :title="$t('browse.units.widgets.deepLTranslate.title')"
      :icon-component="TranslateRound"
    />
  </n-dropdown>
</template>
