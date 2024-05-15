<script setup lang="ts">
import type { Translation } from '@/api';
import { useStateStore } from '@/stores';
import { pickTranslation } from '@/utils';
import { computed } from 'vue';

const props = defineProps<{
  value?: Translation[];
}>();

const state = useStateStore();
const translation = computed(() => pickTranslation(props.value, state.locale));
</script>

<template v-if="translation">
  {{ translation }}
</template>
