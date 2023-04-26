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
  font-size: var(--app-ui-font-size-tiny);
  border-bottom: 1px solid #80808060;
}

.secondary-navbar .navbar-router-link:hover {
  background-color: #80808050;
  border-bottom: 1px solid #80808080;
}

.secondary-navbar .navbar-router-link.router-link-exact-active {
  border-bottom: 1px solid var(--accent-color);
}
</style>
