<script setup lang="ts">
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
</script>

<template>
  <h1>
    {{ $t('search.heading') }}
    <HelpButtonWidget />
  </h1>
  <div class="content-block">
    <p>...</p>
  </div>
</template>

<style scoped></style>
