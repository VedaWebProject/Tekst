<script setup lang="ts">
import type { Component } from 'vue';
import type { RouteLocationRaw } from 'vue-router';
import { NIcon, useThemeVars } from 'naive-ui';

const props = defineProps<{
  label: string;
  route: RouteLocationRaw;
  icon?: Component;
  showIcon?: boolean;
  size?: 'mini' | 'tiny' | 'small' | 'medium' | 'large' | 'huge';
}>();

const themeVars = useThemeVars();
</script>

<template>
  <RouterLink v-slot="{ href, navigate, isActive, isExactActive }" :to="props.route" custom>
    <a :href="href" @click="navigate">
      <div
        :class="[
          'navbar-router-link',
          isActive && 'router-link-active',
          isExactActive && 'router-link-exact-active',
        ]"
      >
        <NIcon v-if="icon && showIcon" :size="20" :component="icon" />
        <span
          class="navbar-router-link-label"
          :style="{ 'font-size': `var(--app-ui-font-size-${props.size || 'small'}` }"
          >{{ props.label }}</span
        >
      </div>
    </a>
  </RouterLink>
</template>

<style scoped>
.navbar-router-link {
  --font-color: v-bind(themeVars.textColor2);
  --transition-curve: v-bind(themeVars.cubicBezierEaseInOut);

  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 0 1rem 0.1rem 1rem;

  font-weight: var(--app-ui-font-weight-normal);
  transition: 0.3s var(--transition-curve);
  color: var(--font-color);
}

.navbar-router-link:hover {
  color: var(--accent-color-fade1);
}

.navbar-router-link.router-link-active,
.navbar-router-link.router-link-exact-active {
  color: var(--accent-color);
}

.navbar-router-link-label {
  text-align: center;
}
</style>
