<script setup lang="ts">
import { useResourcesStore, useStateStore } from '@/stores';
import ResourceCoverageDetailsWidget from '@/components/resource/ResourceCoverageDetailsWidget.vue';
import { NCollapse, NCollapseItem, NSpin, NProgress } from 'naive-ui';
import { computed, onMounted, ref } from 'vue';
import type { AnyResourceRead, ResourceCoverage } from '@/api';

const props = defineProps<{
  resource: AnyResourceRead;
}>();

const emit = defineEmits(['navigate']);

const state = useStateStore();
const resources = useResourcesStore();

const coverage = ref<ResourceCoverage>();
const coveragePercent = computed(() =>
  parseFloat(
    (coverage.value ? (coverage.value.covered / coverage.value.total) * 100 : 0).toFixed(2)
  )
);
const coverageLoading = ref(false);

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
      <resource-coverage-details-widget
        :resource="resource"
        :coverage-data="coverage"
        @navigated="emit('navigate')"
      />
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
</style>
