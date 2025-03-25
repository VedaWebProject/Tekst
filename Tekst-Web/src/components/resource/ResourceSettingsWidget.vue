<script setup lang="ts">
import type { AnyResourceRead } from '@/api';
import ContentContainerHeaderWidget from '@/components/browse/ContentContainerHeaderWidget.vue';
import { SettingsIcon } from '@/icons';
import { useRouter } from 'vue-router';

const props = defineProps<{
  resource: AnyResourceRead;
  full?: boolean;
}>();

const emit = defineEmits(['done']);

const router = useRouter();

function handleClick() {
  router.push({
    name: 'resourceSettings',
    params: {
      textSlug: router.currentRoute.value.params.textSlug,
      id: props.resource.id,
    },
  });
  emit('done');
}
</script>

<template>
  <content-container-header-widget
    v-if="resource.writable"
    :full="full"
    :title="$t('common.settings')"
    :icon-component="SettingsIcon"
    @click="handleClick"
  />
</template>
