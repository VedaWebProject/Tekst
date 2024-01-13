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
const { getSegment } = usePlatformData();
const router = useRouter();
const route = useRoute();

const page = ref<ClientSegmentRead>();

watchEffect(async () => {
  loading.value = true;
  page.value = await getSegment(props.pageKey || String(route.params.p), locale.value);
  if (!page.value) {
    router.replace({ name: 'browse' });
  }
  loading.value = false;
});
</script>

<template>
  <n-spin
    v-if="loading"
    :description="$t('general.loading')"
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
