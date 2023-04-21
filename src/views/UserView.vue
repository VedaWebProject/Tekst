<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const username = computed(() =>
  route.name === 'user' && route.params.username ? String(route.params.username) : undefined
);
</script>

<template>
  <div class="content-block">
    <h1>{{ username }}</h1>
    <p>... public info about {{ username }} ...</p>
  </div>
</template>
