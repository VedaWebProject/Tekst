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
  gap: 12px;
}
</style>

<style>
.secondary-navbar .navbar-router-link {
  padding: 0.3rem 0.5rem;
  border-radius: 4px;
  background-color: #80808030;
}

.secondary-navbar .navbar-router-link:hover {
  background-color: #80808050;
}
</style>
