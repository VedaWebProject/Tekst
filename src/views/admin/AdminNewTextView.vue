<script setup lang="ts">
import { ref } from 'vue';
import {
  NDynamicInput,
  NForm,
  NInput,
  NFormItem,
  NSpace,
  NButton,
  NAlert,
  type FormInst,
} from 'naive-ui';
import type { TextCreate } from '@/openapi';
import { useFormRules } from '@/formRules';
import { useI18n } from 'vue-i18n';
import { useMessages } from '@/messages';
import { useApi } from '@/api';
import { useStateStore } from '@/stores';
import { usePlatformData } from '@/platformData';
import { useRouter } from 'vue-router';
import type { AxiosError } from 'axios';

const initialModel = (): TextCreate => ({
  title: '',
  slug: '',
  levels: ['', ''],
});

const { t } = useI18n({ useScope: 'global' });
const { textFormRules } = useFormRules();
const { textsApi } = useApi();
const router = useRouter();
const { message } = useMessages();
const state = useStateStore();
const { pfData, loadPlatformData } = usePlatformData();
const model = ref<TextCreate>(initialModel());
const formRef = ref<FormInst | null>(null);
const loading = ref(false);

function handleTitleChange(title: string) {
  const tokens = title
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, ' ')
    .trim()
    .split(' ');
  if (tokens.length > 1) {
    model.value.slug = tokens.map((t) => t[0]).join('');
  } else {
    const slug = title.toLowerCase().replace(/[^a-z0-9]+/g, '');
    model.value.slug = slug.substring(0, Math.min(15, slug.length));
  }
}

async function handleSave() {
  loading.value = true;
  try {
    formRef.value
      ?.validate(async (error) => {
        if (error) return;
        try {
          const createdText = (await textsApi.createText({ textCreate: model.value })).data;
          await loadPlatformData();
          state.text = pfData.value?.texts.find((t) => t.slug === createdText.slug) || state.text;
          router.push({ name: 'adminTextsGeneral', params: { text: createdText.slug } });
          message.success(t('admin.newText.msgSaveSuccess', { title: createdText.title }));
        } catch (e) {
          const error = e as AxiosError;
          if (error.response && error.response.status === 409) {
            message.error(t('errors.conflict'));
          } else {
            message.error(t('errors.unexpected'));
          }
        }
      })
      .catch(() => {
        message.error(t('errors.followFormRules'));
      });
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <h1>{{ $t('admin.heading') }}: {{ $t('admin.newText.heading') }}</h1>

  <n-alert :title="$t('general.info')" type="info">
    {{ $t('admin.newText.headerInfoMsg') }}
  </n-alert>

  <div class="content-block">
    <n-form
      ref="formRef"
      :model="model"
      :rules="textFormRules"
      label-placement="top"
      label-width="auto"
      require-mark-placement="right-hanging"
    >
      <n-form-item path="title" :label="$t('models.text.title')">
        <n-input
          v-model:value="model.title"
          type="text"
          :placeholder="$t('models.text.title')"
          @keydown.enter.prevent
          @input="handleTitleChange"
          :disabled="loading"
        />
      </n-form-item>
      <n-form-item path="slug" :label="$t('models.text.slug')">
        <n-input
          v-model:value="model.slug"
          type="text"
          :placeholder="$t('models.text.slug')"
          @keydown.enter.prevent
          :disabled="loading"
        />
      </n-form-item>
      <n-form-item :label="$t('models.text.levels')" required>
        <n-dynamic-input
          v-model:value="model.levels"
          :min="1"
          :max="32"
          item-style="margin-bottom: 0;"
          show-sort-button
          #="{ index }"
        >
          <n-form-item
            ignore-path-change
            :show-label="false"
            :path="`levels[${index}]`"
            :rule="textFormRules.level"
          >
            <n-input
              v-model:value="model.levels[index]"
              type="text"
              :placeholder="$t('models.text.level')"
              @keydown.enter.prevent
              :disabled="loading"
            />
          </n-form-item>
        </n-dynamic-input>
      </n-form-item>
      <n-space :size="12" justify="end" style="margin-top: 0.5rem">
        <n-button block type="primary" @click="handleSave" :loading="loading" :disabled="loading">
          {{ $t('general.saveAction') }}
        </n-button>
      </n-space>
    </n-form>
  </div>
</template>

<style scoped></style>
