<script setup lang="ts">
import { ref } from 'vue';
import { NButton, NIcon, type InputInst } from 'naive-ui';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import GenericModal from '@/components/generic/GenericModal.vue';
import { SearchIcon } from '@/icons';
import NInputOsk from '@/components/NInputOsk.vue';
import { useRouter } from 'vue-router';
import GeneralSearchSettingsForm from '@/forms/search/GeneralSearchSettingsForm.vue';
import QuickSearchSettingsForm from '@/forms/search/QuickSearchSettingsForm.vue';
import { useSearchStore, useStateStore } from '@/stores';

const emit = defineEmits(['submit', 'switchToAdvancedSearch']);

const state = useStateStore();
const search = useSearchStore();
const router = useRouter();

const showModal = ref(false);
const searchInput = ref<string>('');
const inputRef = ref<InputInst>();

function handleSearch(e: UIEvent) {
  e.preventDefault();
  e.stopPropagation();
  showModal.value = false;
  router.push({
    name: 'searchResults',
    query: {
      q: search.encodeQueryParam({
        type: 'quick',
        q: searchInput.value,
        gen: search.settingsGeneral,
        qck: search.settingsQuick,
      }),
    },
  });
  emit('submit');
}

function gotoAdvancedSearch() {
  showModal.value = false;
  router.push({
    name: 'search',
    params: { text: state.text?.slug },
  });
  emit('switchToAdvancedSearch');
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
      <icon-heading level="2" :icon="SearchIcon" style="margin: 0">
        {{ $t('search.quickSearch.heading') }}
        <help-button-widget help-key="quickSearch" />
      </icon-heading>
    </template>

    <n-input-osk
      ref="inputRef"
      v-model="searchInput"
      round
      placeholder="..."
      size="large"
      :max-length="512"
      @keydown.enter="handleSearch"
    >
      <template #prefix>
        <n-icon :component="SearchIcon" size="large" />
      </template>
    </n-input-osk>

    <div class="gray-box">
      <quick-search-settings-form />
      <general-search-settings-form />
    </div>

    <button-shelf top-gap>
      <template #start>
        <n-button text @click="gotoAdvancedSearch">
          {{ $t('search.quickSearch.gotoAdvancedSearch') }}
        </n-button>
      </template>
      <n-button type="primary" @click="handleSearch">{{ $t('search.searchAction') }}</n-button>
    </button-shelf>
  </generic-modal>
</template>

<style scoped></style>
