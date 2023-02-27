<script setup lang="ts">
import { defineProps, type Component } from 'vue';
import { NIcon, useThemeVars } from 'naive-ui';

const props = defineProps<{
  label: string;
  route: string;
  icon?: Component;
}>();

const themeVars = useThemeVars();
</script>

<template>
  <RouterLink
    :to="{ name: props.route }"
    custom
    v-slot="{ href, navigate, isActive, isExactActive }"
  >
    <a :href="href" @click="navigate">
      <div
        :class="[
          'navbar-router-link',
          isActive && 'router-link-active',
          isExactActive && 'router-link-exact-active',
        ]"
      >
        <NIcon :size="20" v-if="props.icon" :component="props.icon" />
        <span class="navbar-router-link-label">{{ props.label }}</span>
      </div>
    </a>
  </RouterLink>
</template>

<style scoped>
.navbar-router-link {
  --font-size: v-bind(themeVars.fontSizeLarge);
  --font-color: v-bind(themeVars.textColor2);
  --transition-curve: v-bind(themeVars.cubicBezierEaseInOut);

  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0.75rem 1.5rem;

  font-weight: normal;
  font-size: var(--font-size);
  transition: 0.3s var(--transition-curve);
  color: var(--font-color);
}

.navbar-router-link:hover,
.navbar-router-link.router-link-active {
  color: var(--accent-color-intense);
}

.navbar-router-link .navbar-router-link-label {
  line-height: 1.75;
}
</style>
