<script setup lang="ts">
import { ref } from 'vue';
import { NButton, NIcon, type InputInst } from 'naive-ui';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import GenericModal from '@/components/generic/GenericModal.vue';
import { SettingsIcon } from '@/icons';
import GeneralSearchSettingsForm from '@/forms/search/GeneralSearchSettingsForm.vue';
import QuickSearchSettingsForm from '@/forms/search/QuickSearchSettingsForm.vue';

const showModal = ref(false);
const inputRef = ref<InputInst>();
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
      <n-icon :component="SettingsIcon" />
    </template>
  </n-button>

  <generic-modal v-model:show="showModal" @after-enter="inputRef?.select()">
    <template #header>
      <icon-heading level="2" :icon="SettingsIcon">
        {{ $t('search.quickSearch.heading') }} – {{ $t('search.settings.heading') }}
      </icon-heading>
    </template>

    <quick-search-settings-form />
    <general-search-settings-form />

    <button-shelf top-gap>
      <n-button type="primary" @click="showModal = false">
        {{ $t('general.okAction') }}
      </n-button>
    </button-shelf>
  </generic-modal>
</template>
