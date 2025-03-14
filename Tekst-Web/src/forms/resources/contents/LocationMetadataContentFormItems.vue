<script setup lang="ts">
import type {
  LocationMetadataContentCreate,
  LocationMetadataResourceRead,
} from '@/api';
import { useResourcesStore } from '@/stores';

const props = defineProps<{
  resource: LocationMetadataResourceRead;
}>();

const model = defineModel<LocationMetadataContentCreate>({ required: true });

const resources = useResourcesStore();

// TODO
</script>

<template>
  <!-- TODO -->
  <div></div>
</template>
