<script setup lang="ts">
import { ref } from 'vue';
import { NButton, NIcon, NModal, NInput } from 'naive-ui';
import ButtonFooter from '@/components/ButtonFooter.vue';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import IconHeading from '@/components/typography/IconHeading.vue';

import SearchRound from '@vicons/material/SearchRound';

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
      <n-icon :component="SearchRound" />
    </template>
  </n-button>

  <n-modal
    v-model:show="showModal"
    preset="card"
    embedded
    header-style="padding-bottom: 1.5rem"
    :auto-focus="false"
    size="large"
    class="tekst-modal"
    to="#app-container"
  >
    <template #header>
      <IconHeading level="1" :icon="SearchRound" style="margin: 0">
        {{ $t('search.quickSearch.heading') }}
        <HelpButtonWidget help-key="quickSearch" />
      </IconHeading>
    </template>

    <n-input round size="large" placeholder="...">
      <template #prefix>
        <n-icon :component="SearchRound" />
      </template>
    </n-input>

    <h3>{{ $t('search.settings.heading') }}</h3>
    <p>Quick Search settings go here...</p>

    <ButtonFooter>
      <n-button secondary :focusable="false" @click="showModal = false">
        {{ $t('general.cancelAction') }}
      </n-button>
      <n-button type="primary">{{ $t('search.searchAction') }}</n-button>
    </ButtonFooter>
  </n-modal>
</template>

<style scoped></style>
