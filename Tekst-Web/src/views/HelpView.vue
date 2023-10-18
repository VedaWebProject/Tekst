<script setup lang="ts">
import { NSpin, NCollapse, NCollapseItem, NInput, NIcon } from 'naive-ui';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import { useHelp, type HelpText } from '@/help';
import { computed, onMounted, ref } from 'vue';

import SearchOutlined from '@vicons/material/SearchOutlined';
import { watch } from 'vue';
import { useStateStore } from '@/stores';

const { getHelpTexts } = useHelp();

const state = useStateStore();
const filter = ref('');
const loading = ref(false);
const helpTexts = ref<[string, HelpText][] | null>(null);
const helpTextsFiltered = computed<[string, HelpText][] | null>(() =>
  filterHelpTexts(helpTexts.value, filter.value)
);

function filterHelpTexts(ht: [string, HelpText][] | null, filter: string): [string, HelpText][] {
  if (!ht) return [];
  if (!filter) return ht;
  return ht.filter((h) => h[1].content.indexOf(filter) !== -1);
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
    <n-collapse v-if="helpTextsFiltered">
      <n-collapse-item
        v-for="[textKey, text] of helpTextsFiltered"
        :key="textKey"
        :title="text.title || textKey"
      >
        <!-- eslint-disable-next-line vue/no-v-html -->
        <div v-html="text.content"></div>
      </n-collapse-item>
    </n-collapse>
    <n-spin v-else-if="loading" />
    <div v-else>
      {{ $t('help.msgNoHelpTextsFound') }}
    </div>
  </div>
</template>

<style scoped></style>
