<script setup lang="ts">
import { useStateStore } from '@/stores';

const state = useStateStore();
</script>

<template>
  <h1>
    {{ $t('admin.heading') }}: {{ state.text?.title }} - {{ $t('admin.texts.nodes.heading') }}
  </h1>

  <div class="content-block">FOO</div>
</template>
