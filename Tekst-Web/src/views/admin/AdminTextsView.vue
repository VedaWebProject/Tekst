<script setup lang="ts">
import { useStateStore } from '@/stores';
import { RouterView } from 'vue-router';

import NavBarRouterLink from '@/components/navigation/NavBarRouterLink.vue';
import SecondaryNavBar from '@/components/navigation/SecondaryNavBar.vue';
import IconHeading from '@/components/typography/IconHeading.vue';

import LibraryBooksOutlined from '@vicons/material/LibraryBooksOutlined';

const state = useStateStore();
</script>

<template>
  <SecondaryNavBar style="margin-top: 0.5rem">
    <NavBarRouterLink
      :label="$t('admin.text.general.heading')"
      :route="{ name: 'adminTextsGeneral', params: { text: state.text?.slug } }"
      size="tiny"
    />
    <NavBarRouterLink
      :label="$t('admin.text.levels.heading')"
      :route="{ name: 'adminTextsLevels', params: { text: state.text?.slug } }"
      size="tiny"
    />
    <NavBarRouterLink
      :label="$t('admin.text.nodes.heading')"
      :route="{ name: 'adminTextsNodes', params: { text: state.text?.slug } }"
      size="tiny"
    />
  </SecondaryNavBar>

  <IconHeading level="1" :icon="LibraryBooksOutlined">
    {{ $t('admin.heading') }}: {{ state.text?.title }}
  </IconHeading>

  <router-view></router-view>
</template>
