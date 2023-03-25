<script setup lang="ts">
import { useBrowseStore } from '@/stores';

const props = defineProps<{ dataId: string }>();
const browse = useBrowseStore();
const data = browse.units[props.dataId];
</script>

<template>
  <div>{{ data.text }}</div>
</template>
