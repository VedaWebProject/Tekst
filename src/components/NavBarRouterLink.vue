<script setup lang="ts">
import type { Component } from 'vue';
import type { RouteLocationRaw } from 'vue-router';
import { NIcon, useThemeVars } from 'naive-ui';

const props = defineProps<{
  label: string;
  route: RouteLocationRaw;
  icon: Component;
  showIcon: boolean;
}>();

const themeVars = useThemeVars();
</script>

<template>
  <RouterLink :to="props.route" custom v-slot="{ href, navigate, isActive, isExactActive }">
    <a :href="href" @click="navigate">
      <div
        :class="[
          'navbar-router-link',
          isActive && 'router-link-active',
          isExactActive && 'router-link-exact-active',
        ]"
      >
        <NIcon :size="20" v-if="props.showIcon" :component="props.icon" />
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
  justify-content: center;
  gap: 8px;
  padding: 0 1rem 0.1rem 1rem;

  font-size: var(--font-size);
  transition: 0.3s var(--transition-curve);
  color: var(--font-color);
}

.navbar-router-link.router-link-active,
.navbar-router-link:hover {
  color: var(--accent-color);
}
</style>
