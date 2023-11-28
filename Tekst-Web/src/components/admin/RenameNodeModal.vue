<script setup lang="ts">
import { PATCH } from '@/api';
import { $t } from '@/i18n';
import type { NodeTreeOption } from '@/views/admin/AdminTextsNodesView.vue';
import { NForm, NFormItem, NModal, NButton, NInput, type InputInst, type FormInst } from 'naive-ui';
import ButtonFooter from '@/components/ButtonFooter.vue';
import { ref } from 'vue';
import { nodeFormRules } from '@/formRules';
import { useModelChanges } from '@/modelChanges';
import { useMessages } from '@/messages';

const props = withDefaults(defineProps<{ show: boolean; node: NodeTreeOption | null }>(), {
  show: false,
});
const emits = defineEmits(['update:show', 'submit']);

const initialNodeModel = () => ({
  label: '',
});

const { message } = useMessages();

const nodeFormRef = ref<FormInst | null>(null);
const nodeFormModel = ref<Record<string, string | null>>(initialNodeModel());
const { changed, getChanges } = useModelChanges(nodeFormModel);

const loading = ref(false);

const nodeRenameInputRef = ref<InputInst | null>(null);

async function handleSubmit() {
  loading.value = true;
  nodeFormRef.value
    ?.validate(async (validationErrors) => {
      if (!validationErrors) {
        const { data, error } = await PATCH('/nodes/{id}', {
          params: { path: { id: props.node?.key?.toString() || '' } },
          body: getChanges(),
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
  <n-modal
    :show="show"
    preset="card"
    class="tekst-modal"
    size="large"
    :bordered="false"
    :closable="false"
    to="#app-container"
    embedded
    @update:show="$emit('update:show', $event)"
    @after-enter="
      () => {
        nodeFormModel.label = props.node?.label || '';
        $nextTick(() => nodeRenameInputRef?.select());
      }
    "
    @after-leave="nodeFormModel.label = ''"
  >
    <h2>{{ $t('admin.text.nodes.rename.heading') }}</h2>

    <n-form
      ref="nodeFormRef"
      :model="nodeFormModel"
      :rules="nodeFormRules"
      label-placement="top"
      label-width="auto"
      require-mark-placement="right-hanging"
    >
      <n-form-item path="label" :label="$t('models.node.label')">
        <n-input
          ref="nodeRenameInputRef"
          v-model:value="nodeFormModel.label"
          type="text"
          :disabled="loading"
          :autofocus="true"
          @keydown.enter="handleSubmit"
        />
      </n-form-item>
    </n-form>
    <ButtonFooter>
      <n-button secondary :disabled="loading" @click="$emit('update:show', false)">
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
    </ButtonFooter>
  </n-modal>
</template>
