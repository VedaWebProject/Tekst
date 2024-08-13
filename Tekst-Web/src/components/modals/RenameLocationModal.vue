<script setup lang="ts">
import { PATCH } from '@/api';
import { $t } from '@/i18n';
import type { LocationTreeOption } from '@/views/admin/AdminTextsLocationsView.vue';
import { NForm, NFormItem, NButton, NInput, type InputInst, type FormInst } from 'naive-ui';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import { ref } from 'vue';
import { locationFormRules } from '@/forms/formRules';
import { useModelChanges } from '@/composables/modelChanges';
import { useMessages } from '@/composables/messages';
import GenericModal from '@/components/generic/GenericModal.vue';
import { EditIcon } from '@/icons';

const props = defineProps<{ location: LocationTreeOption | null }>();
const emit = defineEmits(['submit']);
const show = defineModel<boolean>('show');

const initialLocationModel = () => ({
  label: '',
});

const { message } = useMessages();

const locationFormRef = ref<FormInst | null>(null);
const locationFormModel = ref<Record<string, string | null>>(initialLocationModel());
const { changed, getChanges } = useModelChanges(locationFormModel);

const loading = ref(false);

const locationRenameInputRef = ref<InputInst | null>(null);

async function handleSubmit(e: UIEvent) {
  e.preventDefault();
  e.stopPropagation();
  loading.value = true;
  locationFormRef.value
    ?.validate(async (validationErrors) => {
      if (!validationErrors) {
        const { data, error } = await PATCH('/locations/{id}', {
          params: { path: { id: props.location?.key?.toString() || '' } },
          body: getChanges(),
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
    :title="$t('admin.text.locations.rename.heading')"
    :icon="EditIcon"
    @after-enter="
      () => {
        locationFormModel.label = props.location?.label || '';
        $nextTick(() => locationRenameInputRef?.select());
      }
    "
    @after-leave="locationFormModel.label = ''"
  >
    <n-form
      ref="locationFormRef"
      :model="locationFormModel"
      :rules="locationFormRules"
      label-placement="top"
      :disabled="loading"
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
      <n-button
        type="primary"
        :loading="loading"
        :disabled="loading || !changed"
        @click="handleSubmit"
      >
        {{ $t('general.saveAction') }}
      </n-button>
    </button-shelf>
  </generic-modal>
</template>
