<script setup lang="ts">
import { useBrowseStore } from '@/stores';

const props = defineProps<{ unitId: string }>();
const browse = useBrowseStore();
const data = browse.units[props.unitId];
</script>

<template>
  <div>{{ data.text }}</div>
</template>
