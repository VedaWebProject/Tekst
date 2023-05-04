<script setup lang="ts">
import { useStateStore } from '@/stores';

const state = useStateStore();
</script>

<template>{{ $t('admin.texts.structure.heading') }}: {{ state.text?.title }}</template>
