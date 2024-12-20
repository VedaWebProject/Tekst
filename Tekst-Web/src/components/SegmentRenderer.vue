<script setup lang="ts">
import { usePlatformData } from '@/composables/platformData';
import { useStateStore } from '@/stores';
import { ref, watchEffect } from 'vue';

const props = defineProps<{
  segmentKey: string;
}>();

const { getSegment } = usePlatformData();
const state = useStateStore();

const html = ref<string>();

watchEffect(async () => {
  html.value = (await getSegment(props.segmentKey, state.locale))?.html;
});
</script>

<template>
  <div v-if="html" class="segment-container" v-html="html"></div>
</template>

<style>
.segment-container > p:only-child {
  margin: 0;
}
</style>
