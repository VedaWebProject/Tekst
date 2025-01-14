<script setup lang="ts">
import type { ClientSegmentRead } from '@/api';
import IconHeading from '@/components/generic/IconHeading.vue';
import { usePlatformData } from '@/composables/platformData';
import { useStateStore } from '@/stores';
import { NSpin } from 'naive-ui';
import { ref, watchEffect, type Component } from 'vue';
import { useRouter } from 'vue-router';

const props = defineProps<{
  pageKey?: string;
  icon?: Component;
}>();

const state = useStateStore();
const loading = ref(false);
const { getSegment } = usePlatformData();
const router = useRouter();

const page = ref<ClientSegmentRead>();

watchEffect(async () => {
  loading.value = true;
  page.value = await getSegment(props.pageKey, state.locale);
  if (!page.value) {
    router.replace({ name: 'browse' });
  }
  loading.value = false;
});
</script>

<template>
  <n-spin v-if="loading" :description="$t('general.loading')" class="centered-spinner" />
  <template v-else-if="page">
    <icon-heading v-if="page.title" level="1" :icon="icon">
      {{ page.title }}
    </icon-heading>
    <div class="content-block" style="padding: 1.2rem" v-html="page.html"></div>
  </template>
</template>
