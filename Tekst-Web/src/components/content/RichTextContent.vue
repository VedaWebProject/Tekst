<script setup lang="ts">
import type { RichTextResourceRead } from '@/api';

withDefaults(
  defineProps<{
    resource: RichTextResourceRead;
    reduced?: boolean;
  }>(),
  {
    reduced: false,
  }
);
</script>

<template>
  <div
    v-for="content in resource.contents"
    :key="content.id"
    :class="{
      'rich-text-content-wrapper': resource.contents?.length && resource.contents?.length > 1,
    }"
  >
    <!-- eslint-disable-next-line vue/no-v-html -->
    <div class="rich-text-content" v-html="content.html"></div>
  </div>
</template>

<style scoped>
.rich-text-content-wrapper {
  padding: 1.5rem 0;
  border-bottom: 1px solid var(--main-bg-color);
}
.rich-text-content-wrapper:last-child {
  border-bottom: none;
}
</style>

<style>
.rich-text-content img {
  max-width: 100%;
}
</style>
