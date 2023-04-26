<script setup lang="ts"></script>

<template>
  <div class="secondary-navbar">
    <slot></slot>
  </div>
</template>

<style scoped>
.secondary-navbar {
  display: flex;
  flex-wrap: wrap;
  row-gap: 12px;
}
</style>
