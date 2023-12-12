<script setup lang="ts">
import { NSpin, NModal, NInput, NIcon } from 'naive-ui';
import HelpButtonWidget from '@/components/widgets/HelpButtonWidget.vue';
import { useHelp, type HelpText } from '@/help';
import { computed, onMounted, ref } from 'vue';
import { watch } from 'vue';
import { useStateStore } from '@/stores';

import SearchOutlined from '@vicons/material/SearchOutlined';

const { getHelpTexts } = useHelp();

const state = useStateStore();
const filter = ref('');
const loading = ref(false);
const showModal = ref(false);
const helpTexts = ref<[string, HelpText][] | null>(null);
const helpTextsFiltered = computed<[string, HelpText][] | null>(() =>
  filterHelpTexts(helpTexts.value, filter.value)
);
const helpTextContent = ref<string>();

function filterHelpTexts(ht: [string, HelpText][] | null, filter: string): [string, HelpText][] {
  if (!ht) return [];
  return ht
    .filter((h) => (filter ? h[1].content.indexOf(filter) !== -1 : true))
    .sort((a, b) => (a[1].title || '').localeCompare(b[1].title || ''));
}

async function requestHelpTexts() {
  loading.value = true;
  const ht = await getHelpTexts();
  helpTexts.value = Object.entries(ht).sort((a, b) => a[0].localeCompare(b[0])) as [
    string,
    HelpText,
  ][];
  loading.value = false;
}

function handleClick(e: MouseEvent, textKey: string) {
  e.preventDefault();
  helpTextContent.value = helpTextsFiltered.value?.find((h) => h[0] === textKey)?.[1].content;
  showModal.value = true;
}

onMounted(() => requestHelpTexts());
watch(
  () => state.locale,
  () => {
    filter.value = '';
    requestHelpTexts();
  }
);
</script>

<template>
  <h1>
    Help
    <HelpButtonWidget help-key="helpView" />
  </h1>

  <NInput v-model:value="filter" round :placeholder="$t('search.searchAction')" clearable>
    <template #prefix>
      <n-icon :component="SearchOutlined" />
    </template>
  </NInput>
  <div style="margin-top: 0.5rem">
    {{ $t('help.msgFoundCount', { count: helpTextsFiltered?.length }) }}
  </div>

  <div class="content-block">
    <ul
      v-if="helpTextsFiltered"
      style="display: flex; flex-direction: column; list-style-type: circle"
    >
      <li
        v-for="[textKey, text] of helpTextsFiltered"
        :key="textKey"
        :title="text.title || textKey"
      >
        <a href="#" @click="(e) => handleClick(e, textKey)">{{ text.title || textKey }}</a>
      </li>
    </ul>
    <n-spin v-else-if="loading" />
    <div v-else>
      {{ $t('help.msgNoHelpTextsFound') }}
    </div>
  </div>

  <n-modal
    v-model:show="showModal"
    display-directive="if"
    preset="card"
    class="tekst-modal-wide"
    size="medium"
    :bordered="false"
    :auto-focus="false"
    :closable="true"
    to="#app-container"
    :title="$t('help.help')"
    embedded
    @after-leave="helpTextContent = undefined"
  >
    <!-- eslint-disable-next-line vue/no-v-html -->
    <div v-html="helpTextContent"></div>
  </n-modal>
</template>

<style scoped></style>
