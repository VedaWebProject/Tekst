<script setup lang="ts">
import { useStateStore } from '@/stores';

const state = useStateStore();
</script>

<template>{{ $t('admin.texts.general.heading') }}: {{ state.text?.title }}</template>
