<script setup lang="ts">
import { useStateStore } from '@/stores';
import { RouterView } from 'vue-router';
import NavBarRouterLink from '@/components/navigation/NavBarRouterLink.vue';
import SecondaryNavBar from '@/components/navigation/SecondaryNavBar.vue';
import { useI18n } from 'vue-i18n';

const state = useStateStore();
const { t } = useI18n({ useScope: 'global' });
</script>

<template>
  <SecondaryNavBar style="margin-top: 0.5rem">
    <NavBarRouterLink
      :label="t('admin.texts.general.heading')"
      :route="{ name: 'adminTextsGeneral', params: { text: state.text?.slug } }"
      size="tiny"
    />
    <NavBarRouterLink
      :label="t('admin.texts.levels.heading')"
      :route="{ name: 'adminTextsLevels', params: { text: state.text?.slug } }"
      size="tiny"
    />
    <NavBarRouterLink
      :label="t('admin.texts.nodes.heading')"
      :route="{ name: 'adminTextsNodes', params: { text: state.text?.slug } }"
      size="tiny"
    />
  </SecondaryNavBar>

  <router-view></router-view>
</template>
