<script setup lang="ts">
import { useStats } from '@/stats';
import { computed } from 'vue';
import { NProgress, NButton, NIcon, NSpin } from 'naive-ui';
import RefreshRound from '@vicons/material/RefreshRound';

const { stats, error, load } = useStats();

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
  <h1 style="display: inline; margin-right: 12px">
    {{ $t('administration.heading') }}: {{ $t('administration.overview') }}
  </h1>
  <n-button secondary circle @click="load">
    <template #icon>
      <n-icon :component="RefreshRound" />
    </template>
  </n-button>

  <div v-if="stats && !error" style="margin-top: 1rem">
    <h2>Absolute Numbers</h2>
    <ul>
      <li>Users: {{ counts.users }}</li>
      <li>Texts: {{ counts.texts }}</li>
      <li>Nodes: {{ counts.nodes }}</li>
      <li>Layers: {{ counts.layers }}</li>
    </ul>

    <h2>Layer Types</h2>
    <div v-for="(count, layerType) in layerTypes" style="margin: 12px 0">
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
