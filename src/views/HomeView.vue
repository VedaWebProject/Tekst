<script setup lang="ts"></script>

<template>
  <h1>{{ $t('dummy.home') }}</h1>
  <p>{{ $t('dummy.schiller') }}</p>
  <h2>Accent Colors Test</h2>
  <div class="square" style="background-color: var(--accent-color); color: #000"></div>
  <div class="square" style="background-color: var(--accent-color-fade20); color: #000"></div>
  <div class="square" style="background-color: var(--accent-color-fade40); color: #000"></div>
  <div class="square" style="background-color: var(--accent-color-fade60); color: #000"></div>
  <div class="square" style="background-color: var(--accent-color-fade80); color: #000"></div>
</template>

<style scoped>
.square {
  display: inline-block;
  width: 100px;
  height: 100px;
  margin: 0.5rem;
}
</style>
