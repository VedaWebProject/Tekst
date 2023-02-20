<script setup lang="ts"></script>

<template>
  <h1>{{ $t('dummy.home') }}</h1>
  <p>{{ $t('dummy.schiller') }}</p>
  <h2>Accent Colors Test</h2>
  <div class="square" style="background-color: var(--accent-color-darker); color: #fff">darker</div>
  <div class="square" style="background-color: var(--accent-color-dark); color: #fff">dark</div>
  <div class="square" style="background-color: var(--accent-color); color: #000">plain</div>
  <div class="square" style="background-color: var(--accent-color-light); color: #000">light</div>
  <div class="square" style="background-color: var(--accent-color-lighter); color: #000">
    lighter
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
