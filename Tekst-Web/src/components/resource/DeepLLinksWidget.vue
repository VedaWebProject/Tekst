<script setup lang="ts">
import ContentContainerHeaderWidget from '@/components/browse/ContentContainerHeaderWidget.vue';
import type { AnyResourceRead, DeepLLinksConfig } from '@/api';
import { computed } from 'vue';
import { NDropdown } from 'naive-ui';
import type { DropdownOption } from 'naive-ui';

import { TranslateIcon } from '@/icons';

const DEEPL_TRANSLATOR_URL = 'https://www.deepl.com/translator';

const props = defineProps<{
  widgetConfig: DeepLLinksConfig;
  resource: AnyResourceRead;
  full?: boolean;
}>();

const emit = defineEmits(['done']);

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
    url: `${DEEPL_TRANSLATOR_URL}#${props.widgetConfig.sourceLanguage}/${l}/${contentsTextEncoded.value}`,
  }))
);

const show = computed(
  () =>
    props.widgetConfig?.enabled &&
    props.widgetConfig?.sourceLanguage &&
    props.widgetConfig?.languages?.length &&
    contentsTextEncoded
);

function handleOptionSelect(_: string, option: DropdownOption) {
  emit('done');
  window.open(option.url as string, '_blank', 'noopener noreferrer');
}
</script>

<template>
  <n-dropdown
    v-if="show"
    trigger="click"
    :options="options"
    to="#app-container"
    placement="bottom-start"
    show-arrow
    @select="handleOptionSelect"
  >
    <content-container-header-widget
      :full="full"
      :title="$t('browse.contents.widgets.deepLTranslate.title')"
      :icon-component="TranslateIcon"
    />
  </n-dropdown>
</template>
