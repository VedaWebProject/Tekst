<script setup lang="ts">
import { InfoIcon } from '@lucide/vue';
import { NFlex, NIcon } from 'naive-ui';
</script>

<template>
  <n-flex align="center" size="small" class="text-tiny translucent" :wrap="false">
    <n-icon :component="InfoIcon" />
    {{ $t('common.enterAddsNewEl') }}
  </n-flex>
</template>
