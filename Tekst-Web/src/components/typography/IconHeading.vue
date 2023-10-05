<script setup lang="ts">
import { type Component } from 'vue';
import { NIcon } from 'naive-ui';

withDefaults(
  defineProps<{
    level: '1' | '2' | '3' | '4' | '5' | '6';
    icon?: Component;
    iconSize?: string;
  }>(),
  {
    icon: undefined,
    iconSize: '0.75em',
  }
);
</script>

<template>
  <component :is="`h${level}`">
    <n-icon v-if="icon" :component="icon" :size="iconSize" style="margin-right: 0.5rem" />
    <slot></slot>
  </component>
</template>
