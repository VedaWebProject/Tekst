<script setup lang="ts">
import { usePlatformStore } from '@/stores/platform';
const pf = usePlatformStore();
</script>

<template>
  <h1>{{ pf.get('general.title') }} ({{ $t('dummy.home') }})</h1>
  <p>{{ $t('dummy.schiller') }}</p>
  <h2>Accent Colors Test</h2>
  <div class="square" style="background-color: var(--accent-color); color: #000"></div>
  <div class="square" style="background-color: var(--accent-color-fade1); color: #000"></div>
  <div class="square" style="background-color: var(--accent-color-fade2); color: #000"></div>
  <div class="square" style="background-color: var(--accent-color-fade3); color: #000"></div>
  <div class="square" style="background-color: var(--accent-color-fade4); color: #000"></div>
</template>

<style scoped>
.square {
  display: inline-block;
  width: 100px;
  height: 100px;
  margin: 0.5rem;
}
</style>
