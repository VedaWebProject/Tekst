<script setup lang="ts">
import { type Metadata } from '@/api';
import { useStateStore } from '@/stores';
import { pickTranslation } from '@/utils';
import { computed } from 'vue';

const props = defineProps<{
  data?: Metadata;
  font?: string;
}>();

const state = useStateStore();

const meta = computed(
  () =>
    props.data?.map((meta) => {
      const translation = pickTranslation(
        state.pf?.state.resMetaTranslations.find((tr) => tr.key == meta.key)?.translations,
        state.locale
      );
      return {
        key: translation || meta.key,
        value: meta.value,
        translated: !!translation,
      };
    }) || []
);
</script>

<template>
  <table>
    <tr v-for="m in meta" :key="m.key">
      <td class="metadata-category" :class="{ i: !m.translated }">{{ m.key }}:</td>
      <td :style="{ fontFamily: font }">{{ m.value }}</td>
    </tr>
  </table>
</template>

<style scoped>
table {
  border-collapse: collapse;
}

table td {
  vertical-align: top;
}

table td.metadata-category {
  white-space: nowrap;
  text-transform: capitalize;
  padding-right: var(--gap-sm);
}
</style>
