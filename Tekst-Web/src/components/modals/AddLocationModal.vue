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

const props = defineProps<{ parent: LocationTreeOption | null }>();
const emit = defineEmits(['submit']);
const show = defineModel<boolean>('show');

const initialLocationModel = () => ({
  label: '',
});

const state = useStateStore();
const { message } = useMessages();

const locationFormRef = ref<FormInst | null>(null);
const locationFormModel = ref<Record<string, string | null>>(initialLocationModel());

const loading = ref(false);

const locationRenameInputRef = ref<InputInst | null>(null);

async function handleSubmit(e: UIEvent) {
  e.preventDefault();
  e.stopPropagation();
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
        emit('submit', error ? undefined : data);
        show.value = false;
      }
    })
    .catch(() => {
      message.error($t('errors.followFormRules'));
    });
  loading.value = false;
}
</script>

<template>
  <generic-modal
    v-model:show="show"
    :title="
      $t('admin.text.locations.add.heading', {
        level: state.textLevelLabels[(props.parent?.level ?? -1) + 1],
        parentLabel: props.parent?.label || state.text?.title || '',
      })
    "
    :icon="AddIcon"
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
    <button-shelf top-gap>
      <n-button secondary :disabled="loading" @click="show = false">
        {{ $t('general.cancelAction') }}
      </n-button>
      <n-button type="primary" :loading="loading" :disabled="loading" @click="handleSubmit">
        {{ $t('general.saveAction') }}
      </n-button>
    </button-shelf>
  </generic-modal>
</template>
