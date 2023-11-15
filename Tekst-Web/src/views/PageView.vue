<script setup lang="ts">
import type { ClientSegmentRead } from '@/api';
import { usePlatformData } from '@/platformData';
import { type Component, onBeforeMount } from 'vue';
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { NSpin } from 'naive-ui';
import IconHeading from '@/components/typography/IconHeading.vue';
import { useRouter } from 'vue-router';
import { computed } from 'vue';
import { watchEffect } from 'vue';

const props = defineProps<{
  pageKey?: string;
  icon?: Component;
}>();

const { locale } = useI18n();
const loading = ref(false);
const { pfData, getSegment } = usePlatformData();
const router = useRouter();

const pageKey = computed(() => props.pageKey || router.currentRoute.value.query.p?.toString());
const page = ref<ClientSegmentRead>();

async function loadPage() {
  page.value = await getSegment(pageKey.value, locale.value);
  loading.value = false;
}

onBeforeMount(() => {
  loading.value = true;
  if (
    pageKey.value == 'systemHome' &&
    !pfData.value?.systemSegments.find((p) => p.key === 'systemHome')
  ) {
    router.replace({ name: 'browse' });
    return;
  }
  loadPage();
});

watchEffect(loadPage);
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
  <div v-else class="content-block">{{ $t('errors.notFound') }}</div>
</template>
