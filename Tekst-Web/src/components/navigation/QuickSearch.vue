<script setup lang="ts">
import { ref } from 'vue';
import { NButton, NIcon, NInput } from 'naive-ui';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import GenericModal from '@/components/generic/GenericModal.vue';

import { SearchIcon } from '@/icons';

const showModal = ref(false);
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

  <GenericModal v-model:show="showModal">
    <template #header>
      <IconHeading level="1" :icon="SearchIcon" style="margin: 0">
        {{ $t('search.quickSearch.heading') }}
        <HelpButtonWidget help-key="quickSearch" />
      </IconHeading>
    </template>

    <n-input round size="large" placeholder="...">
      <template #prefix>
        <n-icon :component="SearchIcon" />
      </template>
    </n-input>

    <h3>{{ $t('search.settings.heading') }}</h3>
    <p>Quick Search settings go here...</p>

    <ButtonShelf top-gap>
      <n-button secondary :focusable="false" @click="showModal = false">
        {{ $t('general.cancelAction') }}
      </n-button>
      <n-button type="primary">{{ $t('search.searchAction') }}</n-button>
    </ButtonShelf>
  </GenericModal>
</template>

<style scoped></style>
