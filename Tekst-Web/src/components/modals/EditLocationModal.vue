<script setup lang="ts">
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import GenericModal from '@/components/generic/GenericModal.vue';
import { useMessages } from '@/composables/messages';
import { locationFormRules } from '@/forms/formRules';
import { $t } from '@/i18n';
import { EditIcon } from '@/icons';
import {
  NButton,
  NForm,
  NFormItem,
  NInput,
  NSelect,
  type FormInst,
  type InputInst,
  type SelectOption,
} from 'naive-ui';
import { ref } from 'vue';

export interface EditLocationModalData {
  action: 'add' | 'edit';
  targetId?: string;
  label?: string;
  aliases?: string[] | null;
}

const emit = defineEmits(['submit']);

const { message } = useMessages();

const show = ref(false);
const initialData = (): EditLocationModalData => ({
  action: 'edit',
  targetId: undefined,
  label: undefined,
  aliases: undefined,
});
const data = ref<EditLocationModalData>(initialData());

const locationFormRef = ref<FormInst | null>(null);
const labelInputRef = ref<InputInst | null>(null);

const aliasesOptions = ref<SelectOption[]>([]);

function open(locationData: EditLocationModalData) {
  data.value = { ...locationData };
  aliasesOptions.value = locationData.aliases?.map((a) => ({ label: a, value: a })) || [];
  show.value = true;
}

function handleSubmit() {
  locationFormRef.value
    ?.validate(async (validationErrors) => {
      if (!validationErrors) {
        emit('submit', data.value);
        show.value = false;
      }
    })
    .catch(() => {
      message.error($t('errors.followFormRules'));
    });
}

defineExpose({ open });
</script>

<template>
  <generic-modal
    v-model:show="show"
    :title="
      data.action === 'add'
        ? $t('texts.locations.editOrAdd.headingAdd')
        : $t('texts.locations.editOrAdd.headingEdit')
    "
    :icon="EditIcon"
    @after-enter="
      () => {
        $nextTick(() => labelInputRef?.select());
      }
    "
    @after-leave="data = initialData()"
  >
    <n-form
      ref="locationFormRef"
      :model="data"
      label-placement="top"
      require-mark-placement="right-hanging"
      :rules="locationFormRules"
    >
      <n-form-item :label="$t('common.label')" path="label">
        <n-input
          ref="labelInputRef"
          v-model:value="data.label"
          type="text"
          :autofocus="true"
          @keydown.enter.stop.prevent="handleSubmit"
        />
      </n-form-item>
      <n-form-item :label="$t('models.location.aliases')" path="aliases">
        <n-select
          v-model:value="data.aliases"
          :options="aliasesOptions"
          :placeholder="$t('common.add')"
          tag
          filterable
          multiple
          max-tag-count="responsive"
        />
      </n-form-item>
    </n-form>
    <button-shelf top-gap>
      <n-button secondary @click="show = false">
        {{ $t('common.cancel') }}
      </n-button>
      <n-button type="primary" :disabled="!data.label" @click.stop.prevent="handleSubmit">
        {{ $t('common.save') }}
      </n-button>
    </button-shelf>
  </generic-modal>
</template>
