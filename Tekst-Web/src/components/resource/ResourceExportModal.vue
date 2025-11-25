<script setup lang="ts">
import type { AnyResourceRead } from '@/api';
import GenericModal from '@/components/generic/GenericModal.vue';
import TranslationDisplay from '@/components/generic/TranslationDisplay.vue';
import ResourceExportModalContent from '@/components/resource/ResourceExportModalContent.vue';
import { $t } from '@/i18n';
import { UserIcon } from '@/icons';

defineProps<{ resource: AnyResourceRead }>();
const show = defineModel<boolean>('show');
</script>

<template>
  <generic-modal
    :show="show"
    :title="$t('common.export')"
    :icon="UserIcon"
    @update:show="(v) => (show = v)"
  >
    <div class="mb-md">
      <b>{{ $t('models.resource.modelLabel') }}: </b>
      <translation-display :value="resource.title" />
    </div>
    <resource-export-modal-content v-if="show" :resource="resource" @done="show = false" />
  </generic-modal>
</template>
