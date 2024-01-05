<script setup lang="ts">
import type { PlaintextUnitCreate } from '@/api';
import { NInput, NFormItem } from 'naive-ui';
import { onMounted } from 'vue';

const props = defineProps<{
  model?: PlaintextUnitCreate;
}>();

const emits = defineEmits(['update:model']);

function handleUpdate(field: string, value: any) {
  emits('update:model', {
    ...props.model,
    [field]: value,
  });
}

onMounted(() => {
  if (!props.model) {
    emits('update:model', {
      text: '',
    });
  }
});
</script>

<template>
  <template v-if="model">
    <!-- TEXT -->
    <n-form-item :label="$t('resources.types.plaintext.unitFields.text')">
      <n-input
        type="textarea"
        :rows="4"
        :value="model.text"
        @update:value="(v) => handleUpdate('text', v)"
      />
    </n-form-item>
  </template>
</template>
