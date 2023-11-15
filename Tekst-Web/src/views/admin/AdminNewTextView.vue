<script setup lang="ts">
import { ref } from 'vue';
import {
  NDynamicInput,
  NForm,
  NInput,
  NFormItem,
  NSpace,
  NButton,
  NIcon,
  NAlert,
  type FormInst,
} from 'naive-ui';
import { textFormRules } from '@/formRules';
import { $t } from '@/i18n';
import { useMessages } from '@/messages';
import { POST } from '@/api';
import { useStateStore } from '@/stores';
import { usePlatformData } from '@/platformData';
import { useRouter } from 'vue-router';
import type { TextCreate } from '@/api';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import IconHeading from '@/components/typography/IconHeading.vue';

import AddRound from '@vicons/material/AddRound';
import MinusRound from '@vicons/material/MinusRound';
import AddCircleOutlineRound from '@vicons/material/AddCircleOutlineRound';

interface NewTextModel {
  title?: string;
  slug?: string;
  levels: { locale?: string; label?: string }[][];
}

const initialModel = (): NewTextModel => ({
  title: undefined,
  slug: undefined,
  levels: [[{ locale: state.locale, label: undefined }]],
});

const router = useRouter();
const { message } = useMessages();
const state = useStateStore();
const { pfData, patchPfData } = usePlatformData();
const model = ref<Record<string, any>>(initialModel());
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
      ?.validate(async (validationError) => {
        if (validationError) return;
        const {
          data: createdText,
          error,
          response,
        } = await POST('/texts', { body: model.value as TextCreate });
        if (!error) {
          patchPfData({
            texts: [...(pfData.value?.texts || []), createdText],
          });
          state.text = createdText || state.text;
          router.push({ name: 'adminTextsGeneral', params: { text: createdText.slug } });
          message.success($t('admin.newText.msgSaveSuccess', { title: createdText.title }));
        } else {
          if (response.status === 409) {
            message.error($t('errors.conflict'));
          } else {
            message.error($t('errors.unexpected'), error);
          }
        }
      })
      .catch(() => {
        message.error($t('errors.followFormRules'));
      });
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <IconHeading level="1" :icon="AddCircleOutlineRound">
    {{ $t('admin.newText.heading') }}
    <HelpButtonWidget help-key="adminNewTextView" />
  </IconHeading>

  <n-alert :title="$t('general.info')" type="info" closable>
    {{ $t('admin.newText.headerInfoAlert') }}
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
      <!-- TITLE -->
      <n-form-item path="title" :label="$t('models.text.title')">
        <n-input
          v-model:value="model.title"
          type="text"
          :placeholder="$t('models.text.title')"
          :disabled="loading"
          @keydown.enter.prevent
          @input="handleTitleChange"
        />
      </n-form-item>

      <!-- SLUG -->
      <n-form-item path="slug" :label="$t('models.text.slug')">
        <n-input
          v-model:value="model.slug"
          type="text"
          :placeholder="$t('models.text.slug')"
          :disabled="loading"
          @keydown.enter.prevent
        />
      </n-form-item>

      <!-- STRUCTURE LEVELS -->
      <n-form-item :label="$t('models.text.level', 2)" path="levels" required>
        <n-dynamic-input
          v-model:value="model.levels"
          :min="1"
          :max="32"
          item-style="margin-bottom: 0;"
          :disabled="loading"
          @create="() => [{ locale: state.locale, label: '' }]"
        >
          <template #default="{ index: levelIndex }">
            <div style="padding-right: 12px">{{ levelIndex + 1 }}.</div>
            <div style="flex-grow: 2">
              <!-- STRUCTURE LEVEL LABEL -->
              <n-form-item
                ignore-path-change
                :show-label="false"
                :path="`levels[${levelIndex}][0].label`"
                :rule="textFormRules.levelTranslationLabel"
                style="flex-grow: 2"
              >
                <n-input
                  v-model:value="model.levels[levelIndex][0].label"
                  type="text"
                  :placeholder="$t('models.text.levelLabel')"
                  :disabled="loading"
                  @keydown.enter.prevent
                />
              </n-form-item>
            </div>
          </template>
          <template #action="{ index: indexAction, create, remove }">
            <n-space style="margin-left: 20px; flex-wrap: nowrap">
              <n-button
                secondary
                circle
                :title="$t('general.removeAction')"
                :disabled="model.levels.length === 1"
                @click="() => remove(indexAction)"
              >
                <template #icon>
                  <n-icon :component="MinusRound" />
                </template>
              </n-button>
              <n-button
                secondary
                circle
                :title="$t('general.insertAction')"
                :disabled="model.levels.length >= 32"
                @click="() => create(indexAction)"
              >
                <template #icon>
                  <n-icon :component="AddRound" />
                </template>
              </n-button>
            </n-space>
          </template>
        </n-dynamic-input>
      </n-form-item>
      <n-space :size="12" justify="end" style="margin-top: 0.5rem">
        <n-button block type="primary" :loading="loading" :disabled="loading" @click="handleSave">
          {{ $t('general.saveAction') }}
        </n-button>
      </n-space>
    </n-form>
  </div>
</template>
