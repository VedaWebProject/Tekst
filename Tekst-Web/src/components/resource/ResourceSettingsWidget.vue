<script setup lang="ts">
import type { AnyResourceRead } from '@/api';
import ContentContainerHeaderWidget from '@/components/browse/ContentContainerHeaderWidget.vue';
import { SettingsIcon } from '@/icons';
import { useAuthStore } from '@/stores';
import { computed } from 'vue';
import { useRouter } from 'vue-router';

const props = defineProps<{
  resource: AnyResourceRead;
  full?: boolean;
}>();

const emit = defineEmits(['done']);

const auth = useAuthStore();
const router = useRouter();

const show = computed(
  () =>
    auth.user &&
    ((props.resource.ownerId && auth.user.id === props.resource.ownerId) ||
      props.resource.sharedWrite.includes(auth.user.id) ||
      auth.user.isSuperuser)
);

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
    v-if="show"
    :full="full"
    :title="$t('general.settings')"
    :icon-component="SettingsIcon"
    @click="handleClick"
  />
</template>
