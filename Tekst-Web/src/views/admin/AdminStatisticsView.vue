<script setup lang="ts">
import { useStats } from '@/fetchers';
import { computed } from 'vue';
import { NProgress, NSpin, NStatistic, NIcon } from 'naive-ui';
import { usePlatformData } from '@/platformData';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import IconHeading from '@/components/typography/IconHeading.vue';

import SupervisorAccountRound from '@vicons/material/SupervisorAccountRound';
import LibraryBooksRound from '@vicons/material/LibraryBooksRound';
import AccountTreeRound from '@vicons/material/AccountTreeRound';
import LayersRound from '@vicons/material/LayersRound';
import BarChartRound from '@vicons/material/BarChartRound';

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
  <IconHeading level="1" :icon="BarChartRound">
    {{ $t('admin.statistics.heading') }}
    <HelpButtonWidget help-key="adminStatisticsView" />
  </IconHeading>

  <div v-if="stats && !error" style="margin-top: 1rem">
    <h2>{{ $t('admin.statistics.globalHeading') }}</h2>
    <div class="content-block">
      <div class="statistics-container">
        <n-statistic :label="$t('models.user.modelLabel', 2)" :value="counts.users">
          <template #prefix>
            <n-icon>
              <SupervisorAccountRound />
            </n-icon>
          </template>
        </n-statistic>

        <n-statistic :label="$t('models.text.modelLabel', 2)" :value="counts.texts">
          <template #prefix>
            <n-icon>
              <LibraryBooksRound />
            </n-icon>
          </template>
        </n-statistic>

        <n-statistic :label="$t('models.node.modelLabel', 2)" :value="counts.nodes">
          <template #prefix>
            <n-icon>
              <AccountTreeRound />
            </n-icon>
          </template>
        </n-statistic>

        <n-statistic :label="$t('models.layer.modelLabel', 2)" :value="counts.layers">
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
          :height="18"
          :border-radius="4"
          indicator-placement="inside"
          color="var(--accent-color)"
          rail-color="var(--accent-color-fade4)"
        />
      </div>
    </div>

    <h2>{{ $t('admin.statistics.textsHeading') }}</h2>

    <div v-for="(text, index) in stats.texts" :key="index">
      <div class="content-block">
        <h3>{{ pfData?.texts.find((t) => t.id == text.id)?.title }}</h3>

        <div class="statistics-container">
          <n-statistic :label="$t('models.node.modelLabel', 2)" :value="text.nodesCount">
            <template #prefix>
              <n-icon>
                <AccountTreeRound />
              </n-icon>
            </template>
          </n-statistic>

          <n-statistic :label="$t('models.layer.modelLabel', 2)" :value="text.layersCount">
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
            :height="18"
            :border-radius="4"
            indicator-placement="inside"
            color="var(--accent-color)"
            rail-color="var(--accent-color-fade4)"
          />
        </div>
      </div>
    </div>
  </div>

  <n-spin
    v-else-if="!error"
    :description="$t('init.loading')"
    style="width: 100%; padding: 2rem 0"
  />

  <div v-else>
    {{ $t('errors.error') }}
  </div>
</template>

<style scoped>
.statistics-container {
  display: flex;
  justify-content: flex-start;
  gap: var(--layout-gap);
  flex-wrap: wrap;
}

.statistics-container > * {
  padding: 0.5rem 1rem;
  border: 1px solid var(--main-bg-color);
  border-radius: 4px;
}
</style>
