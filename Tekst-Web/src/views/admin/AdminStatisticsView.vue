<script setup lang="ts">
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import { useStats } from '@/composables/fetchers';
import { NIcon, NProgress, NSpin, NStatistic } from 'naive-ui';
import { computed } from 'vue';

import { BarChartIcon, ResourceIcon, TextsIcon, TreeIcon, UsersIcon } from '@/icons';
import { useStateStore } from '@/stores';

const state = useStateStore();
const { stats, error } = useStats();

const counts = computed(() => ({
  users: stats.value?.usersCount,
  texts: stats.value?.texts.length,
  locations: stats.value?.texts
    .map((t) => t.locationsCount)
    .reduce((total, current) => total + current, 0),
  resources: stats.value?.texts
    .map((t) => t.resourcesCount)
    .reduce((total, current) => total + current, 0),
}));

const resourceTypes = computed(() => {
  const types: Record<string, number> = {};
  stats.value?.texts.forEach((t) => {
    Object.keys(t.resourceTypes).forEach((lt) => {
      types[lt] = lt in types ? types[lt] + t.resourceTypes[lt] : t.resourceTypes[lt];
    });
  });
  return types;
});
</script>

<template>
  <icon-heading level="1" :icon="BarChartIcon">
    {{ $t('admin.statistics.heading') }}
    <help-button-widget help-key="adminStatisticsView" />
  </icon-heading>

  <div v-if="stats && !error" class="mt-lg">
    <h2>{{ $t('admin.statistics.globalHeading') }}</h2>
    <div class="content-block">
      <div class="statistics-container">
        <n-statistic :label="$t('models.user.modelLabel', 2)" :value="counts.users">
          <template #prefix>
            <n-icon :component="UsersIcon" />
          </template>
        </n-statistic>

        <n-statistic :label="$t('models.text.modelLabel', 2)" :value="counts.texts">
          <template #prefix>
            <n-icon :component="TextsIcon" />
          </template>
        </n-statistic>

        <n-statistic :label="$t('models.location.modelLabel', 2)" :value="counts.locations">
          <template #prefix>
            <n-icon :component="TreeIcon" />
          </template>
        </n-statistic>

        <n-statistic :label="$t('models.resource.modelLabel', 2)" :value="counts.resources">
          <template #prefix>
            <n-icon :component="ResourceIcon" />
          </template>
        </n-statistic>
      </div>

      <h3>{{ $t('admin.statistics.resourceTypesHeading') }}</h3>
      <div v-for="(count, resourceType) in resourceTypes" :key="resourceType" class="my-sm">
        <div>{{ $t(`resources.types.${resourceType}.label`) }}: {{ count }}</div>
        <n-progress
          type="line"
          :percentage="parseFloat(((count / (counts.resources || 1)) * 100).toFixed(2))"
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
        <h3>{{ state.textById(text.id)?.title }}</h3>

        <div class="statistics-container">
          <n-statistic :label="$t('models.location.modelLabel', 2)" :value="text.locationsCount">
            <template #prefix>
              <n-icon :component="TreeIcon" />
            </template>
          </n-statistic>

          <n-statistic :label="$t('models.resource.modelLabel', 2)" :value="text.resourcesCount">
            <template #prefix>
              <n-icon :component="ResourceIcon" />
            </template>
          </n-statistic>
        </div>

        <h4>{{ $t('admin.statistics.resourceTypesHeading') }}</h4>
        <template v-for="(count, resourceType) in text.resourceTypes" :key="resourceType">
          <div v-if="count" class="my-sm">
            <div>{{ $t(`resources.types.${resourceType}.label`) }}: {{ count }}</div>
            <n-progress
              type="line"
              :percentage="parseFloat(((count / (text.resourcesCount || 1)) * 100).toFixed(2))"
              :height="18"
              :border-radius="4"
              indicator-placement="inside"
              color="var(--accent-color)"
              rail-color="var(--accent-color-fade4)"
            />
          </div>
        </template>
      </div>
    </div>
  </div>

  <n-spin v-else-if="!error" :description="$t('general.loading')" class="centered-spinner" />

  <div v-else>
    {{ $t('errors.error') }}
  </div>
</template>

<style scoped>
.statistics-container {
  display: flex;
  justify-content: flex-start;
  gap: var(--gap-lg);
  flex-wrap: wrap;
}

.statistics-container > * {
  padding: 0.5rem 1rem;
  border: 1px solid var(--main-bg-color);
  border-radius: 4px;
}
</style>
