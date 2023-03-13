<script setup lang="ts">
import { usePlatformStore } from '@/stores/platform';
const pf = usePlatformStore();
</script>

<template>
  <div class="content-block">
    <h1>{{ pf.data?.info?.platformName }} ({{ $t('dummy.home') }})</h1>
    <p>{{ $t('dummy.schiller') }}</p>

    <h2>Accent Palette Demo</h2>
    <div class="square" style="background-color: #d43a35"></div>
    <div class="square" style="background-color: #476b9a"></div>
    <div class="square" style="background-color: #43895f"></div>
    <div class="square" style="background-color: #dc851f"></div>
    <div class="square" style="background-color: #88447f"></div>

    <h2>Current Accent Color Demo</h2>
    <div class="square" style="background-color: var(--accent-color)"></div>
    <div class="square" style="background-color: var(--accent-color-fade1)"></div>
    <div class="square" style="background-color: var(--accent-color-fade2)"></div>
    <div class="square" style="background-color: var(--accent-color-fade3)"></div>
    <div class="square" style="background-color: var(--accent-color-fade4)"></div>
  </div>
</template>

<style scoped>
.square {
  display: inline-block;
  width: 100px;
  height: 100px;
  margin: 0.5rem;
}
</style>
