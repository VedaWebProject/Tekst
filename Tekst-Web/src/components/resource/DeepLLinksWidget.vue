<script setup lang="ts">
import ContentContainerHeaderWidget from '@/components/browse/ContentContainerHeaderWidget.vue';
import type { AnyResourceRead, DeepLLinksConfig } from '@/api';
import { computed, h } from 'vue';
import type { VNodeChild } from 'vue';
import { useStateStore } from '@/stores';
import { NDropdown } from 'naive-ui';
import type { DropdownOption } from 'naive-ui';

import { TranslateIcon } from '@/icons';

const DEEPL_TRANSLATOR_URL = 'https://www.deepl.com/translator';

const props = defineProps<{
  widgetConfig: DeepLLinksConfig;
  resource: AnyResourceRead;
}>();

const state = useStateStore();

const contentsTextEncoded = computed<string>(() => {
  const contentsText = props.resource.contents
    ?.map((c: Record<string, any>) => c.text as string)
    .join('\n')
    .trim();
  return encodeURIComponent(
    contentsText
      ?.replace(/[^\p{L}\-.?!"\n']+/gu, ' ')
      .replace(/ ?\n ?/g, '\n')
      .trim() || ''
  );
});

const options = computed(() =>
  props.widgetConfig?.languages?.map((l) => ({
    label: l,
    key: l,
  }))
);

const show = computed(
  () =>
    props.widgetConfig?.enabled &&
    props.widgetConfig?.sourceLanguage &&
    props.widgetConfig?.languages?.length &&
    contentsTextEncoded
);

function renderOption(option: DropdownOption) {
  return h(
    'a',
    {
      href: `${DEEPL_TRANSLATOR_URL}#${props.widgetConfig.sourceLanguage}/${option.key}/${contentsTextEncoded.value}`,
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
    v-if="show"
    trigger="click"
    :options="options"
    to="#app-container"
    placement="bottom-start"
    :size="state.dropdownSize"
    :render-label="renderOption"
    show-arrow
  >
    <content-container-header-widget
      :title="$t('browse.contents.widgets.deepLTranslate.title')"
      :icon-component="TranslateIcon"
    />
  </n-dropdown>
</template>
