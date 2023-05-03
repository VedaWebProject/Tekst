<script setup lang="ts">
import { useStats } from '@/fetchers';
import { computed } from 'vue';
import { NProgress, NSpin, NStatistic, NIcon } from 'naive-ui';

import SupervisorAccountRound from '@vicons/material/SupervisorAccountRound';
import LibraryBooksRound from '@vicons/material/LibraryBooksRound';
import AccountTreeRound from '@vicons/material/AccountTreeRound';
import LayersRound from '@vicons/material/LayersRound';
import { usePlatformData } from '@/platformData';

const { pfData } = usePlatformData();
const { stats, error } = useStats();

const counts = computed(() => ({
  users: stats.value?.usersCount,
  texts: stats.value?.texts.length,
  nodes: stats.value?.texts.map((t) => t.nodesCount).reduce((total, current) => total + current, 0),
  layers: stats.value?.texts
    .map((t) => t.layersCount)
    .reduce((total, current) => total + current, 0),
}));

const layerTypes = computed(() => {
  const types: Record<string, number> = {};
  stats.value?.texts.forEach((t) => {
    Object.keys(t.layerTypes).forEach((lt) => {
      types[lt] = lt in types ? types[lt] + t.layerTypes[lt] : t.layerTypes[lt];
    });
  });
  return types;
});
</script>

<template>
  <h1>{{ $t('admin.heading') }}: {{ $t('admin.statistics.heading') }}</h1>

  <div v-if="stats && !error" style="margin-top: 1rem">
    <h2>{{ $t('admin.statistics.globalHeading') }}</h2>
    <div class="content-block">
      <div class="statistics-container">
        <n-statistic :label="$t('internals.users')" :value="counts.users">
          <template #prefix>
            <n-icon>
              <SupervisorAccountRound />
            </n-icon>
          </template>
        </n-statistic>

        <n-statistic :label="$t('internals.texts')" :value="counts.texts">
          <template #prefix>
            <n-icon>
              <LibraryBooksRound />
            </n-icon>
          </template>
        </n-statistic>

        <n-statistic :label="$t('internals.nodes')" :value="counts.nodes">
          <template #prefix>
            <n-icon>
              <AccountTreeRound />
            </n-icon>
          </template>
        </n-statistic>

        <n-statistic :label="$t('internals.layers')" :value="counts.layers">
          <template #prefix>
            <n-icon>
              <LayersRound />
            </n-icon>
          </template>
        </n-statistic>
      </div>

      <h3>{{ $t('admin.statistics.layerTypesHeading') }}</h3>
      <div v-for="(count, layerType) in layerTypes" :key="layerType" style="margin: 12px 0">
        <div>{{ $t(`layerTypes.${layerType}`) }}: {{ count }}</div>
        <n-progress
          type="line"
          :percentage="(count / (counts.layers || 1)) * 100"
          :height="24"
          :border-radius="4"
          indicator-placement="inside"
          color="var(--accent-color-fade4)"
          rail-color="var(--accent-color)"
        />
      </div>
    </div>

    <h2>{{ $t('admin.statistics.textsHeading') }}</h2>

    <div v-for="(text, index) in stats.texts" :key="index">
      <div class="content-block">
        <h3>{{ pfData?.texts.find((t) => t.id == text.id)?.title }}</h3>

        <div class="statistics-container">
          <n-statistic :label="$t('internals.nodes')" :value="text.nodesCount">
            <template #prefix>
              <n-icon>
                <AccountTreeRound />
              </n-icon>
            </template>
          </n-statistic>

          <n-statistic :label="$t('internals.layers')" :value="text.layersCount">
            <template #prefix>
              <n-icon>
                <LayersRound />
              </n-icon>
            </template>
          </n-statistic>
        </div>

        <h4>{{ $t('admin.statistics.layerTypesHeading') }}</h4>
        <div v-for="(count, layerType) in text.layerTypes" :key="layerType" style="margin: 12px 0">
          <div>{{ $t(`layerTypes.${layerType}`) }}: {{ count }}</div>
          <n-progress
            type="line"
            :percentage="(count / (text.layersCount || 1)) * 100"
            :height="24"
            :border-radius="4"
            indicator-placement="inside"
            color="var(--accent-color-fade4)"
            rail-color="var(--accent-color)"
          />
        </div>
      </div>
    </div>
  </div>

  <div v-else-if="!error" style="padding: 2rem; text-align: center">
    <n-spin>
      <template #description>
        {{ $t('init.loading') }}
      </template>
    </n-spin>
  </div>

  <div v-else>
    {{ $t('errors.error') }}
  </div>
</template>

<style scoped>
.statistics-container {
  display: flex;
  justify-content: flex-start;
  gap: var(--content-padding);
  flex-wrap: wrap;
}

.statistics-container > * {
  padding: 0.5rem 1rem;
  background-color: var(--main-bg-color);
  border-radius: 4px;
}
</style>
