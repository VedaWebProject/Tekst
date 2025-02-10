<script setup lang="ts">
import { deeplTargetLanguages, type AnyResourceRead, type DeepLLinksConfig } from '@/api';
import ContentContainerHeaderWidget from '@/components/browse/ContentContainerHeaderWidget.vue';
import { TranslateIcon } from '@/icons';
import { NPopselect } from 'naive-ui';
import type { SelectBaseOption } from 'naive-ui/es/select/src/interface';
import { computed } from 'vue';

const DEEPL_TRANSLATOR_URL = 'https://www.deepl.com/translator';

const props = defineProps<{
  config: DeepLLinksConfig;
  resource: AnyResourceRead;
  full?: boolean;
}>();

const emit = defineEmits(['done']);

const contentsTextEncoded = computed<string>(() => {
  const contentsText = props.resource.contents
    ?.map((c: Record<string, unknown>) => c.text as string)
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
  deeplTargetLanguages.map((l) => ({
    label: l,
    value: l,
    url: `${DEEPL_TRANSLATOR_URL}#${props.config.sourceLanguage}/${l}/${contentsTextEncoded.value}`,
  }))
);

const show = computed(
  () => props.config.enabled && props.config.sourceLanguage && contentsTextEncoded.value
);

function handleOptionSelect(_: string, option: SelectBaseOption) {
  window.open(option.url as string, '_blank', 'noopener noreferrer');
  emit('done');
}
</script>

<template>
  <n-popselect
    v-if="show"
    trigger="click"
    :options="options"
    placement="bottom-start"
    :z-index="1800"
    scrollable
    @update:value="handleOptionSelect"
  >
    <template #header>
      <span class="b">
        {{ $t('browse.contents.widgets.deeplTranslate.title') }}
      </span>
    </template>
    <content-container-header-widget
      :full="full"
      :title="$t('browse.contents.widgets.deeplTranslate.title')"
      :icon-component="TranslateIcon"
    />
  </n-popselect>
</template>
