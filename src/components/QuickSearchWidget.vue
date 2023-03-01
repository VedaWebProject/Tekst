<script setup lang="ts">
import { ref } from 'vue';
import { NButton, NIcon, NModal } from 'naive-ui';
import SearchRound from '@vicons/material/SearchRound';

const showModal = ref(false);
</script>

<template>
  <n-button
    secondary
    circle
    size="large"
    icon-placement="left"
    @click="showModal = true"
    :title="$t('general.quickSearch')"
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
    size="huge"
    style="width: 600px; max-width: 95%"
  >
    <h2>{{ $t('general.quickSearch') }}</h2>
    Quick search form goes here...
    <div style="text-align: right; margin-top: 1rem">
      <n-button type="primary">{{ $t('general.searchAction') }}</n-button>
    </div>
  </n-modal>
</template>

<style scoped></style>
