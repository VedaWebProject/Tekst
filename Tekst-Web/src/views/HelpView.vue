<script setup lang="ts">
import GenericModal from '@/components/generic/GenericModal.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import { useHelp } from '@/composables/help';
import { useStateStore } from '@/stores';
import { NIcon, NInput, NSpin } from 'naive-ui';
import { computed, onMounted, ref, watch } from 'vue';

import type { HelpText } from '@/composables/help';
import { QuestionMarkIcon, SearchIcon } from '@/icons';

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

function handleClick(textKey: string) {
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
  <icon-heading level="1" :icon="QuestionMarkIcon">
    {{ $t('help.help') }}
    <help-button-widget help-key="helpView" />
  </icon-heading>

  <n-input v-model:value="filter" round :placeholder="$t('search.searchAction')" clearable>
    <template #prefix>
      <n-icon :component="SearchIcon" />
    </template>
  </n-input>

  <div class="text-small translucent mt-lg">
    {{ $t('help.msgFoundCount', { count: helpTextsFiltered?.length }) }}
  </div>

  <div class="content-block">
    <ul v-if="helpTextsFiltered">
      <li
        v-for="[textKey, text] of helpTextsFiltered"
        :key="textKey"
        :title="text.title || textKey"
        class="mb-sm"
      >
        <span class="help-topic" @click.stop.prevent="handleClick(textKey)">
          {{ text.title || textKey }}
        </span>
      </li>
    </ul>
    <n-spin v-else-if="loading" class="centered-spinner" />
    <div v-else>
      {{ $t('help.msgNoHelpTextsFound') }}
    </div>
  </div>

  <generic-modal
    v-model:show="showModal"
    width="wide"
    :title="$t('help.help')"
    :icon="QuestionMarkIcon"
    heading-level="3"
    @after-leave="helpTextContent = undefined"
  >
    <!-- eslint-disable-next-line vue/no-v-html -->
    <div v-html="helpTextContent"></div>
  </generic-modal>
</template>

<style scoped>
.help-topic {
  cursor: pointer;
  transition: color 0.2s;
}

.help-topic:hover {
  color: var(--accent-color);
}
</style>
