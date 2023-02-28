<script setup lang="ts">
import { usePlatformStore } from '@/stores/platform';
const pf = usePlatformStore();
</script>

<template>
  <h1>{{ pf.get('info.platformName') }} ({{ $t('dummy.home') }})</h1>
  <p>{{ $t('dummy.schiller') }}</p>

  <h2>Accent Palette Demo</h2>
  <div class="square" style="background-color: #334195"></div>
  <div class="square" style="background-color: #bc243b"></div>
  <div class="square" style="background-color: #e4572e"></div>
  <div class="square" style="background-color: #18a058"></div>
  <div class="square" style="background-color: #9368b7"></div>

  <h2>Current Accent Color Demo</h2>
  <div class="square" style="background-color: var(--accent-color)"></div>
  <div class="square" style="background-color: var(--accent-color-fade1)"></div>
  <div class="square" style="background-color: var(--accent-color-fade2)"></div>
  <div class="square" style="background-color: var(--accent-color-fade3)"></div>
  <div class="square" style="background-color: var(--accent-color-fade4)"></div>
</template>

<style scoped>
.square {
  display: inline-block;
  width: 100px;
  height: 100px;
  margin: 0.5rem;
}
</style>
