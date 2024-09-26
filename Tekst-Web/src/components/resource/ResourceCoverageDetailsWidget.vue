<script setup lang="ts">
import { NThing, NVirtualList } from 'naive-ui';
import { computed } from 'vue';
import { type AnyResourceRead, type ResourceCoverage } from '@/api';
import { useRoute } from 'vue-router';
import { useStateStore } from '@/stores';
import router from '@/router';
import { pickTranslation } from '@/utils';

const props = defineProps<{
  resource: AnyResourceRead;
  coverageData?: ResourceCoverage;
}>();

const emit = defineEmits(['navigated']);

const state = useStateStore();
const route = useRoute();

const coverageListItems = computed(
  () =>
    props.coverageData?.details.map((parent) => ({
      title: state.textLevelLabels[props.resource.level - 1]
        ? `${state.textLevelLabels[props.resource.level - 1]}: ${parent.label}`
        : pickTranslation(props.resource.title, state.locale),
      extra: `${parent.locations.filter((loc) => loc.covered).length}/${parent.locations.length}`,
      locations: parent.locations,
    })) || []
);

function handleLocationClick(level: number, position: number) {
  router.push({
    name: 'browse',
    params: { text: route.params.text },
    query: {
      lvl: level,
      pos: position,
    },
  });
  emit('navigated');
}
</script>

<template>
  <div class="gray-box">
    <n-virtual-list
      style="max-height: 768px"
      :item-size="42"
      :items="coverageListItems"
      item-resizable
    >
      <template #default="{ item }">
        <n-thing>
          <template #header>
            <span style="font-weight: var(--font-weight-normal)">
              {{ item.title }}
            </span>
          </template>
          <template #header-extra>
            <span class="mr-lg"> ({{ item.extra }}) </span>
          </template>
          <template #description>
            <div class="cov-block">
              <div
                v-for="location in item.locations"
                :key="location.position"
                class="cov-box"
                :class="location.covered && 'covered'"
                :title="`${state.textLevelLabels[resource.level]}: ${location.label}`"
                @click="() => handleLocationClick(resource.level, location.position)"
              ></div>
            </div>
          </template>
        </n-thing>
      </template>
    </n-virtual-list>
  </div>
</template>

<style scoped>
.cov-block {
  margin: 0.25rem 0 0.75rem 0;
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
.cov-box {
  width: 16px;
  height: 16px;
  background-color: var(--col-error);
  border-radius: 2px;
  opacity: 0.75;
  transition: 0.2s;
  cursor: pointer;
}
.cov-box:hover {
  opacity: 1;
}

.cov-box.covered {
  background-color: var(--col-success);
}
</style>
