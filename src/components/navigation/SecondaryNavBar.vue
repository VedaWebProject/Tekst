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
  padding: 0.3rem;
  margin: 0 0.5rem;
  font-size: var(--app-ui-font-size-tiny);
  border-bottom: 2px solid transparent;
}

.secondary-navbar .navbar-router-link:hover {
  border-bottom: 2px solid transparent;
}

.secondary-navbar .navbar-router-link.router-link-exact-active {
  border-bottom: 2px solid var(--accent-color);
}
</style>
