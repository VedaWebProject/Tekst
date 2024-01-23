<script setup lang="ts">
import type { Translation } from '@/api';
import { pickTranslation } from '@/utils';
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';

const props = defineProps<{
  value?: Translation[];
}>();

const { locale } = useI18n();
const translation = computed(() => pickTranslation(props.value, locale.value));
</script>

<template v-if="translation">
  {{ translation }}
</template>
