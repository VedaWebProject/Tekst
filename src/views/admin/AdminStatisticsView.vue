<script setup lang="ts">
import { useStats } from '@/stats';
import { computed } from 'vue';
import { NProgress, NSpin } from 'naive-ui';
import { usePlatformStore } from '@/stores';

const pf = usePlatformStore();
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
      <h3>{{ $t('admin.statistics.absoluteNumbersHeading') }}</h3>
      <ul>
        <li>{{ $t('internals.users') }}: {{ counts.users }}</li>
        <li>{{ $t('internals.texts') }}: {{ counts.texts }}</li>
        <li>{{ $t('internals.nodes') }}: {{ counts.nodes }}</li>
        <li>{{ $t('internals.layers') }}: {{ counts.layers }}</li>
      </ul>

      <h3>{{ $t('admin.statistics.layerTypesHeading') }}</h3>
      <div v-for="(count, layerType) in layerTypes" :key="layerType" style="margin: 12px 0">
        <div>{{ $t(`layerTypes.${layerType}`) }}: {{ count }}</div>
        <n-progress
          type="line"
          :percentage="(count / (counts.layers || 1)) * 100"
          :height="32"
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
        <h3>{{ pf.data?.texts.find((t) => t.id == text.id)?.title }}</h3>
        <ul>
          <li>{{ $t('internals.nodes') }}: {{ text.nodesCount }}</li>
          <li>{{ $t('internals.layers') }}: {{ text.layersCount }}</li>
        </ul>
        <h4>{{ $t('admin.statistics.layerTypesHeading') }}</h4>
        <div v-for="(count, layerType) in text.layerTypes" :key="layerType" style="margin: 12px 0">
          <div>{{ $t(`layerTypes.${layerType}`) }}: {{ count }}</div>
          <n-progress
            type="line"
            :percentage="(count / (text.layersCount || 1)) * 100"
            :height="16"
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

<style scoped></style>
