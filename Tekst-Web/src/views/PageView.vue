<script setup lang="ts">
import type { ClientSegmentRead } from '@/api';
import { usePlatformData } from '@/platformData';
import { watch, type Component } from 'vue';
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { NSpin } from 'naive-ui';
import IconHeading from '@/components/typography/IconHeading.vue';
import { useRoute } from 'vue-router';

const props = defineProps<{
  pageKey?: string;
  icon?: Component;
}>();

const { locale } = useI18n();
const loading = ref(false);
const { getSegment } = usePlatformData();
const route = useRoute();
const page = ref<ClientSegmentRead>();

watch(
  [() => props.pageKey, () => route.query.p, () => locale.value],
  async ([propKey, queryKey, nextLocale]) => {
    loading.value = true;
    page.value = (await getSegment(propKey || queryKey?.toString(), nextLocale)) || undefined;
    loading.value = false;
  },
  { immediate: true }
);
</script>

<template>
  <n-spin
    v-if="loading"
    :description="$t('init.loading')"
    style="width: 100%; display: flex; justify-content: center"
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
