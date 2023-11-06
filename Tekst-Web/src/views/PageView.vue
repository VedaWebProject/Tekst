<script setup lang="ts">
import type { ClientSegmentRead } from '@/api';
import { usePlatformData } from '@/platformData';
import { watchEffect, type Component } from 'vue';
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { NSpin } from 'naive-ui';
import IconHeading from '@/components/typography/IconHeading.vue';

const props = defineProps<{
  pageKey: string;
  icon: Component;
}>();

const { locale } = useI18n();
const loading = ref(false);
const { getSegment } = usePlatformData();
const page = ref<ClientSegmentRead>();

watchEffect(async () => {
  loading.value = true;
  page.value = (await getSegment(props.pageKey, locale.value)) || undefined;
  loading.value = false;
});
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
