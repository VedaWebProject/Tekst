<script setup lang="ts">
import { useStateStore } from '@/stores';
import { RouterView } from 'vue-router';

import IconHeading from '@/components/typography/IconHeading.vue';
import LibraryBooksOutlined from '@vicons/material/LibraryBooksOutlined';

const state = useStateStore();
</script>

<template>
  <IconHeading level="1" :icon="LibraryBooksOutlined">
    {{ state.text?.title }}
  </IconHeading>
  <router-view></router-view>
</template>
