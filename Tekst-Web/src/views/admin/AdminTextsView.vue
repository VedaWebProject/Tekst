<script setup lang="ts">
import { useStateStore } from '@/stores';
import { RouterView } from 'vue-router';
import IconHeading from '@/components/generic/IconHeading.vue';

import { TextsIcon } from '@/icons';

const state = useStateStore();
</script>

<template>
  <IconHeading level="1" :icon="TextsIcon">
    {{ state.text?.title }}
  </IconHeading>
  <router-view></router-view>
</template>
