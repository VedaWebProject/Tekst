<script setup lang="ts">
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import GenericModal from '@/components/generic/GenericModal.vue';
import { $t } from '@/i18n';
import { ArchiveIcon } from '@/icons';
import { NButton, NDatePicker, NIcon } from 'naive-ui';
import { ref } from 'vue';

const props = defineProps<{
  default?: number;
}>();

const emit = defineEmits<{
  submit: [value: number | undefined];
}>();

const showModal = ref(false);
const ts = ref<number>(props.default ?? new Date().getTime());

function handleWidgetClick() {
  ts.value = props.default ?? new Date().getTime();
  showModal.value = true;
}

function handleSubmit() {
  const date = new Date(ts.value);
  const now = new Date();
  if (
    date.getFullYear() === now.getFullYear() &&
    date.getMonth() === now.getMonth() &&
    date.getDate() === now.getDate()
  ) {
    emit('submit', undefined);
  } else {
    emit('submit', ts.value);
  }
  showModal.value = false;
}
</script>

<template>
  <n-button
    secondary
    size="tiny"
    :focusable="false"
    :title="$t('contents.archive.widgetTip')"
    @click.stop.prevent="handleWidgetClick"
  >
    <template #icon>
      <n-icon :component="ArchiveIcon" />
    </template>
    {{ $t('contents.archive.widgetTitle') }}
  </n-button>

  <generic-modal
    v-model:show="showModal"
    :title="$t('contents.archive.widgetTitle')"
    :icon="ArchiveIcon"
  >
    <n-date-picker
      v-model:value="ts"
      panel
      input-readonly
      size="large"
      type="date"
      :is-date-disabled="(timestamp: number) => timestamp > Date.now()"
    />
    <button-shelf class="mt-lg">
      <n-button secondary @click="showModal = false">
        {{ $t('common.cancel') }}
      </n-button>
      <n-button type="primary" @click="handleSubmit">
        {{ $t('common.ok') }}
      </n-button>
    </button-shelf>
  </generic-modal>
</template>
