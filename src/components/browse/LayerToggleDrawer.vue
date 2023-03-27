<script setup lang="ts">
import { computed } from 'vue';
import { NDrawer, NDrawerContent } from 'naive-ui';

const props = defineProps<{ show: boolean }>();
const emits = defineEmits<{ (e: 'update:show', show: boolean): void }>();

const show = computed({
  get() {
    return props.show;
  },
  set(value) {
    emits('update:show', value);
  },
});
</script>

<template>
  <n-drawer v-model:show="show" :width="512" :auto-focus="false" style="max-width: 90%">
    <n-drawer-content title="Toggle Data Layers" :native-scrollbar="false" closable>
      ...
    </n-drawer-content>
  </n-drawer>
</template>
