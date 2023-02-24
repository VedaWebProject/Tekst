<script setup lang="ts">
import { defineProps, type Component } from 'vue';
import { NIcon, useThemeVars } from 'naive-ui';

defineProps<{
  label: string;
  route: string;
  icon?: Component;
}>();

const themeVars = useThemeVars();
</script>

<template>
  <RouterLink
    :to="{ name: $props.route }"
    custom
    v-slot="{ href, navigate, isActive, isExactActive }"
  >
    <a :href="href" @click="navigate">
      <div
        :class="[
          'main-nav-router-link',
          isActive && 'router-link-active',
          isExactActive && 'router-link-exact-active',
        ]"
      >
        <NIcon :size="20" v-if="$props.icon" :component="$props.icon" />
        <span class="main-nav-router-link-label">{{ $props.label }}</span>
      </div>
    </a>
  </RouterLink>
</template>

<style scoped>
.main-nav-router-link {
  --font-size: v-bind(themeVars.fontSizeLarge);
  --font-color: v-bind(themeVars.textColor2);
  --transition-curve: v-bind(themeVars.cubicBezierEaseInOut);

  display: flex;
  align-items: center;
  gap: 8px;
  margin-right: 1.5rem;
  padding: 0.2rem;

  font-weight: normal;
  font-size: var(--font-size);
  transition: 0.3s var(--transition-curve);
  color: var(--font-color);
}

.main-nav-router-link:hover {
  color: #0f0;
}

.main-nav-router-link.router-link-active {
  color: #f00;
}

.main-nav-router-link .main-nav-router-link-label {
  line-height: 1.75;
}
</style>
