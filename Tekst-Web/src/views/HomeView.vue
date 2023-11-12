<script setup lang="ts">
import { usePlatformData } from '@/platformData';

const { pfData } = usePlatformData();
</script>

<template>
  <div class="content-block">
    <h1>{{ pfData?.settings.infoPlatformName }} ({{ $t('dummy.home') }})</h1>
    <p>{{ $t('dummy.schiller') }}</p>

    <h2>Accent Palette Demo</h2>
    <div class="square" style="background-color: #305d97"></div>
    <div class="square" style="background-color: #097f86"></div>
    <div class="square" style="background-color: #43895f"></div>
    <div class="square" style="background-color: #d49101"></div>
    <div class="square" style="background-color: #d26e2b"></div>
    <div class="square" style="background-color: #d43a35"></div>
    <div class="square" style="background-color: #b83e63"></div>
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
  width: 60px;
  height: 60px;
  margin: 0.5rem;
}
</style>
