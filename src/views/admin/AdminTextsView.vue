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
  <h1>{{ $t('admin.heading') }}: {{ state.text?.title }}</h1>

  <SecondaryNavBar align="flex-start">
    <NavBarRouterLink
      :label="$t('admin.texts.general.heading')"
      :route="{ name: 'adminTextsGeneral', params: { text: state.text?.slug } }"
    />
    <NavBarRouterLink
      :label="$t('admin.texts.levels.heading')"
      :route="{ name: 'adminTextsLevels', params: { text: state.text?.slug } }"
    />
    <NavBarRouterLink
      :label="$t('admin.texts.nodes.heading')"
      :route="{ name: 'adminTextsNodes', params: { text: state.text?.slug } }"
    />
  </SecondaryNavBar>

  <div class="content-block">
    <router-view></router-view>
  </div>
</template>
