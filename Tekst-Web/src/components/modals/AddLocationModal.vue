<script setup lang="ts">
import { POST } from '@/api';
import { $t } from '@/i18n';
import type { LocationTreeOption } from '@/views/admin/AdminTextsLocationsView.vue';
import { NForm, NFormItem, NButton, NInput, type InputInst, type FormInst } from 'naive-ui';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import { nextTick, ref } from 'vue';
import { locationFormRules } from '@/forms/formRules';
import { useStateStore } from '@/stores';
import { useMessages } from '@/composables/messages';
import GenericModal from '@/components/generic/GenericModal.vue';
import { AddIcon } from '@/icons';

const props = withDefaults(defineProps<{ show: boolean; parent: LocationTreeOption | null }>(), {
  show: false,
});
const emits = defineEmits(['update:show', 'submit']);

const initialLocationModel = () => ({
  label: '',
});

const state = useStateStore();
const { message } = useMessages();

const locationFormRef = ref<FormInst | null>(null);
const locationFormModel = ref<Record<string, string | null>>(initialLocationModel());

const loading = ref(false);

const locationRenameInputRef = ref<InputInst | null>(null);

async function handleSubmit() {
  loading.value = true;
  locationFormRef.value
    ?.validate(async (validationErrors) => {
      if (!validationErrors) {
        const { data, error } = await POST('/locations', {
          body: {
            label: locationFormModel.value.label || '',
            level: (props.parent?.level ?? -1) + 1,
            position: Number.MAX_SAFE_INTEGER,
            textId: state.text?.id || '',
            parentId: props.parent?.key?.toString() || null,
          },
        });
        emits('submit', error ? undefined : data);
        emits('update:show', false);
      }
    })
    .catch(() => {
      message.error($t('errors.followFormRules'));
    });
  loading.value = false;
}
</script>

<template>
  <GenericModal
    :show="show"
    :title="
      $t('admin.text.locations.add.heading', {
        level: state.textLevelLabels[(props.parent?.level ?? -1) + 1],
        parentLabel: props.parent?.label || state.text?.title || '',
      })
    "
    :icon="AddIcon"
    @update:show="$emit('update:show', $event)"
    @after-enter="nextTick(() => locationRenameInputRef?.focus())"
    @after-leave="locationFormModel.label = ''"
  >
    <n-form
      ref="locationFormRef"
      :model="locationFormModel"
      :rules="locationFormRules"
      :disabled="loading"
      label-placement="top"
      label-width="auto"
      require-mark-placement="right-hanging"
    >
      <n-form-item path="label" :label="$t('models.location.label')">
        <n-input
          ref="locationRenameInputRef"
          v-model:value="locationFormModel.label"
          type="text"
          :autofocus="true"
          @keydown.enter="handleSubmit"
        />
      </n-form-item>
    </n-form>
    <ButtonShelf top-gap>
      <n-button secondary :disabled="loading" @click="$emit('update:show', false)">
        {{ $t('general.cancelAction') }}
      </n-button>
      <n-button type="primary" :loading="loading" :disabled="loading" @click="handleSubmit">
        {{ $t('general.saveAction') }}
      </n-button>
    </ButtonShelf>
  </GenericModal>
</template>