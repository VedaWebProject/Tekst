<template>
  <div class="secondary-navbar-wrapper">
    <div class="secondary-navbar">
      <slot></slot>
    </div>
  </div>
</template>

<style scoped>
.secondary-navbar-wrapper {
  display: flex;
  justify-content: space-around;
  align-items: center;
}
.secondary-navbar {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 12px;
  background-color: var(--accent-color-fade5);
  padding-top: 3px;
  border-radius: 4px;
}
</style>

<style>
.secondary-navbar .navbar-router-link {
  font-size: var(--app-ui-font-size-small);
  padding: 0.3rem;
  margin: 0 0.5rem;
  border-bottom: 3px solid transparent;
}

.secondary-navbar .navbar-router-link.router-link-exact-active {
  border-bottom: 3px solid var(--accent-color);
}
</style>
