<script setup lang="ts">
import UnitContainerHeaderWidget from '@/components/browse/UnitContainerHeaderWidget.vue';
import TranslateRound from '@vicons/material/TranslateRound';
import type { DeepLLinksConfig } from '@/openapi';
import { computed, h } from 'vue';
import type { VNodeChild } from 'vue';
import { useStateStore } from '@/stores';
import { NDropdown } from 'naive-ui';
import type { DropdownOption } from 'naive-ui';

const props = defineProps<{
  widgetConfig: DeepLLinksConfig;
  layer: Record<string, any>;
}>();

const state = useStateStore();

const options = computed(() =>
  props.widgetConfig?.languages?.map((l) => ({
    label: l,
    key: l,
  }))
);

function renderOption(option: DropdownOption) {
  const text = encodeURIComponent(
    String(props.layer.unit.text)
      .replace(/[^\p{L}\-.?!"']+/gu, ' ')
      .replace(/[ \t\r]+/g, ' ')
      .trim()
  );
  return h(
    'a',
    {
      href: `https://www.deepl.com/translator#${props.widgetConfig.sourceLanguage}/${option.key}/${text}`,
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
    v-if="props.widgetConfig?.enabled && props.layer.unit.text && props.widgetConfig"
    trigger="click"
    :options="options"
    placement="bottom-start"
    :size="state.dropdownSize"
    :render-label="renderOption"
    show-arrow
  >
    <UnitContainerHeaderWidget
      :title="$t('browse.units.widgets.deepLTranslate.title')"
      :iconComponent="TranslateRound"
    />
  </n-dropdown>
</template>
