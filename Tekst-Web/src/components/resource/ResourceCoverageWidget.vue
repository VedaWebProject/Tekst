<script setup lang="ts">
import type { AnyResourceRead, ResourceCoverage } from '@/api';
import { useResourcesStore, useStateStore } from '@/stores';
import { pickTranslation } from '@/utils';
import { NCollapse, NCollapseItem, NProgress, NSpin, NThing, NVirtualList } from 'naive-ui';
import { computed, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';

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
  props.resource.coverage
    ? parseFloat(((props.resource.coverage[0] / props.resource.coverage[1]) * 100).toFixed(2))
    : null
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

function handleDetailsLocationClick(locId: string) {
  router.push({
    name: 'browse',
    params: {
      textSlug: route.params.textSlug,
      locId,
    },
  });
  emit('navigate');
}

async function loadCoverageData() {
  coverageLoading.value = true;
  coverage.value = await resources.getCoverage(props.resource.id);
  coverageLoading.value = false;
}
</script>

<template>
  <div>
    <n-collapse
      accordion
      default-expanded-names="overview"
      @update:expanded-names="loadCoverageData"
    >
      <n-collapse-item
        :title="$t('browse.contents.widgets.infoWidget.coverageOverview')"
        name="overview"
      >
        <template v-if="resource.coverage">
          <div class="text-small mb-sm">
            {{
              $t('browse.contents.widgets.infoWidget.coverageStatement', {
                present: resource.coverage[0],
                total: resource.coverage[1],
                level: state.textLevelLabels[resource.level],
              })
            }}
          </div>
          <n-progress
            v-if="coveragePercent !== null"
            type="line"
            :percentage="coveragePercent"
            :height="16"
            :border-radius="3"
            indicator-placement="inside"
            color="var(--primary-color)"
            rail-color="var(--primary-color-fade4)"
          />
        </template>
        <i v-else class="translucent text-medium">{{ $t('errors.notFound') }}</i>
      </n-collapse-item>
      <n-collapse-item
        :title="$t('browse.contents.widgets.infoWidget.coverageRanges')"
        name="ranges"
      >
        <template v-if="coverage && !coverageLoading">
          <div
            v-if="coverage.rangesCovered"
            class="text-small mb-sm"
            :style="{ color: 'var(--success-color)' }"
          >
            {{ $t('browse.contents.widgets.infoWidget.coverageRangesPresent') }}
          </div>
          <div v-else class="text-small mb-sm" :style="{ color: 'var(--error-color)' }">
            {{ $t('browse.contents.widgets.infoWidget.coverageRangesMissing') }}
          </div>
          <div class="gray-box">
            <n-virtual-list
              style="max-height: 512px"
              :item-size="42"
              :items="coverage.ranges"
              item-resizable
            >
              <template #default="{ item: range }">
                <div class="range">
                  <code class="text-small">{{ range[0] }}</code>
                  <template v-if="range[0] !== range[1]">
                    <b class="mx-sm">...</b>
                    <code class="text-small">{{ range[1] }}</code>
                  </template>
                </div>
              </template>
            </n-virtual-list>
          </div>
        </template>
        <n-spin v-else-if="coverageLoading" class="centered-spinner" />
        <i v-else class="translucent text-medium">{{ $t('errors.notFound') }}</i>
      </n-collapse-item>
      <n-collapse-item
        :title="$t('browse.contents.widgets.infoWidget.coverageDetails')"
        name="details"
      >
        <div v-if="coverage && !coverageLoading" class="gray-box">
          <n-virtual-list
            style="max-height: 512px"
            :item-size="42"
            :items="coverageDetailsItems"
            item-resizable
          >
            <template #default="{ item }">
              <n-thing>
                <template #header>
                  <span class="n">
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
                      :key="location.id"
                      class="cov-box"
                      :style="{
                        backgroundColor: location.covered
                          ? 'var(--success-color)'
                          : 'var(--error-color)',
                      }"
                      :title="`${state.textLevelLabels[resource.level]}: ${location.label}`"
                      @click="() => handleDetailsLocationClick(location.locId)"
                    ></div>
                  </div>
                </template>
              </n-thing>
            </template>
          </n-virtual-list>
        </div>
        <n-spin v-else-if="coverageLoading" class="centered-spinner" />
        <i v-else class="translucent text-medium">{{ $t('errors.notFound') }}</i>
      </n-collapse-item>
    </n-collapse>
  </div>
</template>

<style scoped>
.range {
  border-bottom: 1px solid var(--main-bg-color);
  padding: 0.5rem 0;
}

.range:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.range:first-child {
  padding-top: 0;
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
  border-radius: 2px;
  opacity: 0.75;
  transition: 0.2s;
  cursor: pointer;
}

.cov-box:hover {
  opacity: 1;
}
</style>
