<script setup lang="ts">
import type { ClientSegmentRead } from '@/api';
import { usePlatformData } from '@/platformData';
import { ref, type Component, watchEffect } from 'vue';
import { useI18n } from 'vue-i18n';
import { NSpin } from 'naive-ui';
import IconHeading from '@/components/typography/IconHeading.vue';
import { useRoute, useRouter } from 'vue-router';

const props = defineProps<{
  pageKey?: string;
  icon?: Component;
}>();

const { locale } = useI18n();
const loading = ref(false);
const { systemHome, getSegment } = usePlatformData();
const router = useRouter();
const route = useRoute();

const page = ref<ClientSegmentRead>();

async function loadPage(pageKey: string | undefined, locale: string) {
  loading.value = true;
  page.value = await getSegment(pageKey, locale);
  if (!page.value) {
    router.replace({ name: 'browse' });
  }
  loading.value = false;
}

watchEffect(() => {
  loading.value = true;
  if (!(route.name === 'info' || route.name === 'home')) {
    return;
  }
  if (route.name === 'home' && !systemHome.value) {
    router.replace({ name: 'browse' });
    return;
  }
  loadPage(props.pageKey || String(route.params.p), locale.value);
});
</script>

<template>
  <n-spin
    v-if="loading"
    :description="$t('init.loading')"
    style="width: 100%; display: flex; justify-content: center; padding: var(--layout-gap) 0"
  />
  <template v-else-if="page">
    <IconHeading v-if="page.title" level="1" :icon="icon">
      {{ page.title }}
    </IconHeading>
    <!-- eslint-disable-next-line vue/no-v-html -->
    <div class="content-block" v-html="page.html"></div>
  </template>
</template>
