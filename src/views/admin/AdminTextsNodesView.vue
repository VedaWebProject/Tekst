<script setup lang="ts">
import { useStateStore } from '@/stores';

const state = useStateStore();
</script>

<template>{{ $t('models.node.modelLabel', 2) }}: {{ state.text?.title }}</template>
