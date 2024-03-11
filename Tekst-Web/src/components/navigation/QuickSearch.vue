<script setup lang="ts">
import { ref } from 'vue';
import { NCollapse, NCollapseItem, NButton, NIcon, type InputInst } from 'naive-ui';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import GenericModal from '@/components/generic/GenericModal.vue';
import { SearchIcon } from '@/icons';
import NInputOsk from '@/components/NInputOsk.vue';
import { useRouter } from 'vue-router';
import { Base64 } from 'js-base64';
import { useStateStore } from '@/stores';
import type { SearchRequestBody } from '@/api';
import GeneralSearchSettingsForm from '@/forms/search/GeneralSearchSettingsForm.vue';
import QuickSearchSettingsForm from '@/forms/search/QuickSearchSettingsForm.vue';

const showModal = ref(false);
const searchInput = ref<string>('');
const router = useRouter();
const state = useStateStore();

const inputRef = ref<InputInst>();
const settingsExpanded = ref<string[]>([]);

function handleSubmit(e: UIEvent) {
  e.preventDefault();
  e.stopPropagation();
  showModal.value = false;
  const reqBody: SearchRequestBody = {
    searchType: 'quick',
    query: searchInput.value,
    settingsGeneral: state.searchSettingsGeneral,
    settingsQuick: state.searchSettingsQuick,
  };
  router.push({
    name: 'searchResults',
    params: {
      req: Base64.encode(JSON.stringify(reqBody), true),
    },
  });
}
</script>

<template>
  <n-button
    secondary
    circle
    size="large"
    icon-placement="left"
    :title="$t('search.quickSearch.heading')"
    :focusable="false"
    @click="showModal = true"
  >
    <template #icon>
      <n-icon :component="SearchIcon" />
    </template>
  </n-button>

  <generic-modal v-model:show="showModal" @after-enter="inputRef?.select()">
    <template #header>
      <icon-heading level="1" :icon="SearchIcon" style="margin: 0">
        {{ $t('search.quickSearch.heading') }}
        <help-button-widget help-key="quickSearch" />
      </icon-heading>
    </template>

    <n-input-osk
      ref="inputRef"
      v-model:value="searchInput"
      round
      placeholder="..."
      size="large"
      style="margin-bottom: var(--layout-gap)"
      @keydown.enter="handleSubmit"
    >
      <template #prefix>
        <n-icon :component="SearchIcon" />
      </template>
    </n-input-osk>

    <n-collapse v-model:expanded-names="settingsExpanded">
      <n-collapse-item :title="$t('search.settings.heading')" name="settings">
        <quick-search-settings-form />
        <general-search-settings-form />
      </n-collapse-item>
    </n-collapse>

    <button-shelf top-gap>
      <n-button secondary @click="showModal = false">
        {{ $t('general.cancelAction') }}
      </n-button>
      <n-button type="primary" @click="handleSubmit">{{ $t('search.searchAction') }}</n-button>
    </button-shelf>
  </generic-modal>
</template>

<style scoped></style>
