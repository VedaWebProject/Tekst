<script setup lang="ts">
import { useResourcesStore, useStateStore } from '@/stores';
import { NThing, NVirtualList, NCollapse, NCollapseItem, NSpin, NProgress } from 'naive-ui';
import { computed, onMounted, ref } from 'vue';
import type { AnyResourceRead, ResourceCoverage } from '@/api';
import { useRoute, useRouter } from 'vue-router';
import { pickTranslation } from '@/utils';

const props = defineProps<{
  resource: AnyResourceRead;
}>();

const emit = defineEmits(['navigate']);

const state = useStateStore();
const router = useRouter();
const route = useRoute();
const resources = useResourcesStore();

const coverage = ref<ResourceCoverage>();
const coveragePercent = computed(() =>
  parseFloat(
    (coverage.value ? (coverage.value.covered / coverage.value.total) * 100 : 0).toFixed(2)
  )
);
const coverageLoading = ref(false);

const coverageDetailsItems = computed(
  () =>
    coverage.value?.details.map((parent) => ({
      title: state.textLevelLabels[props.resource.level - 1]
        ? `${state.textLevelLabels[props.resource.level - 1]}: ${parent.label}`
        : pickTranslation(props.resource.title, state.locale),
      extra: `${parent.locations.filter((loc) => loc.covered).length}/${parent.locations.length}`,
      locations: parent.locations,
    })) || []
);

function handleDetailsLocationClick(level: number, position: number) {
  router.push({
    name: 'browse',
    params: { text: route.params.text },
    query: {
      lvl: level,
      pos: position,
    },
  });
  emit('navigate');
}

onMounted(async () => {
  coverageLoading.value = true;
  coverage.value = await resources.getCoverage(props.resource.id);
  coverageLoading.value = false;
});
</script>

<template>
  <n-collapse v-if="coverage && !coverageLoading" accordion default-expanded-names="overview">
    <n-collapse-item
      :title="$t('browse.contents.widgets.infoWidget.coverageOverview')"
      name="overview"
    >
      <div class="text-small mb-sm">
        {{
          $t('browse.contents.widgets.infoWidget.coverageStatement', {
            present: coverage.covered,
            total: coverage.total,
            level: state.textLevelLabels[resource.level],
          })
        }}
      </div>
      <n-progress
        type="line"
        :percentage="coveragePercent"
        :height="16"
        :border-radius="3"
        indicator-placement="inside"
        color="var(--accent-color)"
        rail-color="var(--accent-color-fade4)"
      />
    </n-collapse-item>
    <n-collapse-item :title="$t('browse.contents.widgets.infoWidget.coverageRanges')" name="ranges">
      <div v-if="coverage.rangesCovered" class="text-small mb-sm" style="color: var(--col-success)">
        {{ $t('browse.contents.widgets.infoWidget.coverageRangesPresent') }}
      </div>
      <div v-else class="text-small mb-sm" style="color: var(--col-error)">
        {{ $t('browse.contents.widgets.infoWidget.coverageRangesMissing') }}
      </div>
      <ul class="m-0">
        <li v-for="(range, index) in coverage.ranges" :key="`${index}_${range.toString()}`">
          <span class="range-boundary">{{ range[0] }}</span>
          <template v-if="range[0] !== range[1]">
            <span class="mx-sm">–</span>
            <span class="range-boundary">{{ range[1] }}</span>
          </template>
        </li>
      </ul>
    </n-collapse-item>
    <n-collapse-item
      :title="$t('browse.contents.widgets.infoWidget.coverageDetails')"
      name="details"
    >
      <div class="gray-box">
        <n-virtual-list
          style="max-height: 512px"
          :item-size="42"
          :items="coverageDetailsItems"
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
                    @click="() => handleDetailsLocationClick(resource.level, location.position)"
                  ></div>
                </div>
              </template>
            </n-thing>
          </template>
        </n-virtual-list>
      </div>
    </n-collapse-item>
  </n-collapse>
  <n-spin v-else-if="coverageLoading" class="centered-spinner" />
</template>

<style scoped>
.range-boundary {
  padding: 0 var(--gap-sm);
  background-color: var(--main-bg-color);
  border-radius: var(--border-radius);
}
:deep(.n-collapse-item__content-inner) {
  padding-top: var(--gap-sm) !important;
}

/** Coverage details */

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
