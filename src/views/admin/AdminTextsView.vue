<script setup lang="ts">
import { useStateStore } from '@/stores';
import { NTabs, NTab } from 'naive-ui';
import { useRouter } from 'vue-router';
import { RouterView } from 'vue-router';

const state = useStateStore();
const router = useRouter();

function handleTabSwitch(selectedTabName: string) {
  router.push({ name: selectedTabName, params: { text: state.text?.slug } });
}
</script>

<template>
  <h1>{{ $t('admin.heading') }}: {{ $t('admin.texts.heading') }}</h1>

  <div class="content-block">
    <h2>{{ state.text?.title }}</h2>
    <n-tabs
      type="card"
      default-value="adminTexts"
      size="large"
      tab-style="font-weight: var(--app-ui-font-weight-normal)"
      @update:value="handleTabSwitch"
    >
      <n-tab name="adminTexts">{{ $t('admin.texts.general.heading') }}</n-tab>
      <n-tab name="adminTextsStructure">{{ $t('admin.texts.structure.heading') }}</n-tab>
    </n-tabs>
    <router-view></router-view>
  </div>
</template>
