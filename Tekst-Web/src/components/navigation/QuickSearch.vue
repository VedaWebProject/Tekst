<script setup lang="ts">
import { ref } from 'vue';
import { NButton, NIcon } from 'naive-ui';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import GenericModal from '@/components/generic/GenericModal.vue';
import { SearchIcon } from '@/icons';
import NInputOsk from '@/components/NInputOsk.vue';
import { useRouter } from 'vue-router';
import { Base64 } from 'js-base64';

const showModal = ref(false);
const searchInput = ref<string>();
const router = useRouter();

function handleSubmit(e: UIEvent) {
  e.preventDefault();
  e.stopPropagation();
  showModal.value = false;
  router.push({
    name: 'searchResults',
    params: { query: Base64.encode(searchInput.value || '', true) },
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

  <generic-modal v-model:show="showModal">
    <template #header>
      <icon-heading level="1" :icon="SearchIcon" style="margin: 0">
        {{ $t('search.quickSearch.heading') }}
        <help-button-widget help-key="quickSearch" />
      </icon-heading>
    </template>

    <n-input-osk v-model:value="searchInput" round placeholder="..." @keydown.enter="handleSubmit">
      <template #prefix>
        <n-icon :component="SearchIcon" />
      </template>
    </n-input-osk>

    <h3>{{ $t('search.settings.heading') }}</h3>
    <p>Quick Search settings go here...</p>

    <button-shelf top-gap>
      <n-button secondary @click="showModal = false">
        {{ $t('general.cancelAction') }}
      </n-button>
      <n-button type="primary" @click="handleSubmit">{{ $t('search.searchAction') }}</n-button>
    </button-shelf>
  </generic-modal>
</template>

<style scoped></style>
