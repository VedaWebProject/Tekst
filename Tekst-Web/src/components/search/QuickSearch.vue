<script setup lang="ts">
import { computed, ref } from 'vue';
import { NFlex, NIcon, NAutoComplete, type AutoCompleteOption } from 'naive-ui';
import { SearchIcon } from '@/icons';
import NInputOsk from '@/components/NInputOsk.vue';
import { useRouter } from 'vue-router';
import { useSearchStore } from '@/stores';
import QuickSearchSettings from '@/components/search/QuickSearchSettings.vue';
import type { LocationRead } from '@/api';

const search = useSearchStore();
const router = useRouter();

const searchInput = ref<string>('');
const locations = ref<LocationRead[]>([]);

const options = computed<AutoCompleteOption[]>(() => [
  ...(searchInput.value
    ? [
        {
          value: searchInput.value,
          label: `SEARCH FOR: ${searchInput.value}`,
        },
      ]
    : []),
  ...(locations.value.length
    ? locations.value.map((l) => ({
        value: l.id,
        label: `GO TO LOCATION: ${l.label}`,
        textId: l.textId,
        level: l.level,
        position: l.position,
      }))
    : []),
]);

function handleSelect(input: string) {
  router.push({
    name: 'searchResults',
    query: {
      q: search.encodeQueryParam({
        type: 'quick',
        q: searchInput.value,
        gen: search.settingsGeneral,
        qck: search.settingsQuick,
      }),
    },
  });
}
</script>

<template>
  <n-flex id="quick-search" :wrap="false">
    <n-auto-complete
      v-model:value="searchInput"
      :options="options"
      :to="false"
      :menu-props="{ style: { position: 'relative', bottom: '-50px' } }"
      @select="handleSelect"
    >
      <template #default="{ handleInput, handleBlur, handleFocus, value: slotValue }">
        <n-input-osk
          :model-value="slotValue"
          round
          placeholder="..."
          size="large"
          :max-length="512"
          @input="handleInput"
          @focus="handleFocus"
          @blur="handleBlur"
        >
          <template #prefix>
            <n-icon :component="SearchIcon" size="large" />
          </template>
        </n-input-osk>
      </template>
    </n-auto-complete>
    <quick-search-settings />
  </n-flex>
</template>

<style scoped></style>
