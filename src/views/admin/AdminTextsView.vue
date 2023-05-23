<script setup lang="ts">
import { useStateStore } from '@/stores';
// import { NTabs, NTab } from 'naive-ui';
// import { useRouter } from 'vue-router';
import { RouterView } from 'vue-router';
import NavBarRouterLink from '@/components/navigation/NavBarRouterLink.vue';
import SecondaryNavBar from '@/components/navigation/SecondaryNavBar.vue';

const state = useStateStore();
// const router = useRouter();

// function handleTabSwitch(selectedTabName: string) {
//   router.push({ name: selectedTabName, params: { text: state.text?.slug } });
// }
</script>

<template>
  <h1>{{ $t('admin.heading') }}: {{ $t('admin.texts.heading') }}</h1>
  <h2>{{ state.text?.title }}</h2>

  <SecondaryNavBar align="flex-start">
    <NavBarRouterLink
      :label="$t('admin.texts.general.heading')"
      :route="{ name: 'adminTextsGeneral', params: { text: state.text?.slug } }"
    />
    <NavBarRouterLink
      :label="$t('admin.texts.structure.heading')"
      :route="{ name: 'adminTextsStructure', params: { text: state.text?.slug } }"
    />
  </SecondaryNavBar>

  <!-- <n-tabs
    type="segment"
    default-value="adminTexts"
    size="large"
    :bar-width="0"
    tab-style="font-weight: var(--app-ui-font-weight-normal)"
    @update:value="handleTabSwitch"
  >
    <n-tab name="adminTexts">{{ $t('admin.texts.general.heading') }}</n-tab>
    <n-tab name="adminTextsStructure">{{ $t('admin.texts.structure.heading') }}</n-tab>
  </n-tabs> -->
  <div class="content-block">
    <router-view></router-view>
  </div>
</template>
