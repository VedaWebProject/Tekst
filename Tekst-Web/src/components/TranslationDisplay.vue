<script setup lang="ts">
import type { Translation } from '@/api';
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';

const props = defineProps<{
  value?: Translation[];
}>();

const { locale } = useI18n();
const translation = computed(
  () =>
    (
      props.value?.find((t) => t.locale === locale.value) ||
      props.value?.find((t) => t.locale === '*') ||
      props.value?.find((t) => t.locale === 'enUS') ||
      props.value?.[0]
    )?.translation
);
</script>

<template v-if="translation">
  {{ translation }}
</template>
