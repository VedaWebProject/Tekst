<script setup lang="ts">
import type {
  AnnotationAggregation,
  LocationMetadataResourceRead,
  LocationMetadataSearchQuery,
} from '@/api';
import { useResourcesStore } from '@/stores';
import { onMounted, ref } from 'vue';

const props = defineProps<{
  resource: LocationMetadataResourceRead;
  queryIndex: number;
}>();
const model = defineModel<LocationMetadataSearchQuery>({ required: true });

const resources = useResourcesStore();
const aggregations = ref<AnnotationAggregation[]>([]);

onMounted(async () => {
  aggregations.value = await resources.getAggregations(props.resource.id);
});
</script>

<template>
  <!-- TODO -->
  <div></div>
</template>
