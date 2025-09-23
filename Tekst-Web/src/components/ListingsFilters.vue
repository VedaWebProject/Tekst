<script setup lang="ts">
import { FilterIcon, SearchIcon, UndoIcon } from '@/icons';
import {
  NButton,
  NCollapse,
  NCollapseItem,
  NFlex,
  NIcon,
  NInput,
  NSelect,
  type InputInst,
} from 'naive-ui';
import { computed, nextTick, onMounted, ref } from 'vue';

const props = defineProps<{ flagsLabels: Record<string, string> }>();
const search = defineModel<string | undefined>('search', { required: false, default: undefined });
const flags = defineModel<string[]>('flags', { required: false, default: () => [] });
const emit = defineEmits(['changed']);

const searchInputRef = ref<InputInst | null>(null);

const flagsOptions = computed(() =>
  Object.entries(props.flagsLabels).map(([k, v]) => ({ label: v, value: k }))
);
const isUnfiltered = computed(
  () => !search.value && flags.value.length === Object.keys(props.flagsLabels).length
);

function reset() {
  search.value = undefined;
  flags.value = Object.entries(props.flagsLabels).map(([k]) => k);
}

function handleFilterCollapseItemClick(data: { name: string; expanded: boolean }) {
  if (data.name === 'filters') {
    if (data.expanded) {
      nextTick(() => searchInputRef.value?.focus());
    } else {
      reset();
    }
  }
}

defineExpose({ reset });

onMounted(() => {
  reset();
});
</script>

<template>
  <div class="gray-box">
    <n-collapse @item-header-click="handleFilterCollapseItemClick">
      <n-collapse-item name="filters">
        <template #header>
          <n-flex align="center" :wrap="false" inline>
            <n-icon :component="FilterIcon" class="translucent" />
            <span>
              {{ $t('common.filters') }}
              <template v-if="isUnfiltered">({{ $t('common.off') }})</template>
            </span>
          </n-flex>
        </template>

        <n-input
          ref="searchInputRef"
          v-model:value="search"
          :placeholder="$t('common.searchAction')"
          class="mb-md"
          round
          @update:value="emit('changed')"
        >
          <template #prefix>
            <n-icon :component="SearchIcon" />
          </template>
        </n-input>
        <n-select
          v-model:value="flags"
          :options="flagsOptions"
          multiple
          @update:value="emit('changed')"
        />
        <n-flex justify="flex-end">
          <n-button secondary class="mt-md" @click="reset">
            {{ $t('common.reset') }}
            <template #icon>
              <n-icon :component="UndoIcon" />
            </template>
          </n-button>
        </n-flex>
      </n-collapse-item>
    </n-collapse>
  </div>
</template>
