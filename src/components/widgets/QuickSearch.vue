<script setup lang="ts">
import { ref } from 'vue';
import { NButton, NIcon, NModal, NInput } from 'naive-ui';
import SearchRound from '@vicons/material/SearchRound';
import ModalButtonFooter from '@/components/ModalButtonFooter.vue';

const showModal = ref(false);
</script>

<template>
  <n-button
    secondary
    circle
    size="large"
    icon-placement="left"
    @click="showModal = true"
    :title="$t('search.quickSearch.heading')"
    :focusable="false"
  >
    <template #icon>
      <n-icon :component="SearchRound" />
    </template>
  </n-button>

  <n-modal
    v-model:show="showModal"
    preset="card"
    embedded
    :closable="false"
    size="large"
    class="textrig-modal"
  >
    <h2>{{ $t('search.quickSearch.heading') }}</h2>

    <n-input round size="large" :placeholder="$t('search.quickSearch.heading')">
      <template #prefix>
        <n-icon :component="SearchRound" />
      </template>
    </n-input>

    <h3>{{ $t('search.settings.heading') }}</h3>
    <p>Quick Search settings go here...</p>

    <ModalButtonFooter>
      <n-button @click="showModal = false" :focusable="false">
        {{ $t('general.cancelAction') }}
      </n-button>
      <n-button type="primary">{{ $t('search.searchAction') }}</n-button>
    </ModalButtonFooter>
  </n-modal>
</template>

<style scoped></style>
