<script setup lang="ts">
import { deeplTargetLanguages, type AnyResourceRead } from '@/api';
import ContentContainerHeaderWidget from '@/components/browse/ContentContainerHeaderWidget.vue';
import { LanguagesIcon, SearchIcon } from '@/icons';
import { NIcon, NInput, NPopselect } from 'naive-ui';
import type { SelectBaseOption } from 'naive-ui/es/select/src/interface';
import { computed, nextTick, ref } from 'vue';

const DEEPL_TRANSLATOR_URL = 'https://www.deepl.com/translator';

const props = defineProps<{
  resource: AnyResourceRead;
  full?: boolean;
}>();

const emit = defineEmits(['done']);

const filterInputRef = ref();
const filterStr = ref('');

const config = computed(() =>
  props.resource.resourceType === 'plainText' ? props.resource.config.special.deeplLinks : null
);

const contentsTextEncoded = computed<string>(() => {
  const contentsText = props.resource.contents
    ?.map((c) => (c?.text ?? '') as string)
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
  config.value
    ? deeplTargetLanguages
        .filter((l) => l.toLowerCase().includes(filterStr.value.toLowerCase()))
        .map((l) => ({
          label: l,
          value: l,
          url: `${DEEPL_TRANSLATOR_URL}#${config.value?.sourceLanguage}/${l}/${contentsTextEncoded.value}`,
        }))
    : []
);

const show = computed(
  () => config.value?.enabled && config.value.sourceLanguage && contentsTextEncoded.value
);

function handleOptionSelect(_: string, option: SelectBaseOption) {
  window.open(option.url as string, '_blank', 'noreferrer');
  emit('done');
}

async function handleUpdateShow(show: boolean) {
  if (!show) {
    filterStr.value = '';
  } else {
    nextTick(() => filterInputRef.value.focus());
  }
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
    @update:show="handleUpdateShow"
  >
    <template #header>
      <span class="b">
        {{ $t('browse.contents.widgets.deeplTranslate.title') }}
      </span>
      <n-input
        ref="filterInputRef"
        v-model:value="filterStr"
        round
        clearable
        :placeholder="$t('common.search')"
        class="my-sm"
      >
        <template #prefix>
          <n-icon :component="SearchIcon" />
        </template>
      </n-input>
    </template>
    <content-container-header-widget
      :full="full"
      :title="$t('browse.contents.widgets.deeplTranslate.title')"
      :icon-component="LanguagesIcon"
    />
  </n-popselect>
</template>
