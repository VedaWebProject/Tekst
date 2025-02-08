<script setup lang="ts">
import type { TextCreate } from '@/api';
import { POST } from '@/api';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import { useMessages } from '@/composables/messages';
import { usePlatformData } from '@/composables/platformData';
import DynamicInputControls from '@/forms/DynamicInputControls.vue';
import { textFormRules } from '@/forms/formRules';
import { $t } from '@/i18n';
import { AddCircleIcon } from '@/icons';
import { useStateStore } from '@/stores';
import { NAlert, NButton, NDynamicInput, NForm, NFormItem, NInput, type FormInst } from 'naive-ui';
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const initialModel = (): TextCreate => ({
  title: '',
  slug: '',
  levels: [[{ locale: '*', translation: '' }]],
  accentColor: '#43895F',
  defaultLevel: 0,
  fullLocLabelAsHitHeading: false,
  isActive: false,
  labeledLocation: true,
  locDelim: '; ',
  resourceCategories: [],
  subtitle: [],
});

const router = useRouter();
const { message } = useMessages();
const state = useStateStore();
const { loadPlatformData } = usePlatformData();
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
      ?.validate(async (validationError) => {
        if (validationError) return;
        const { data: createdText, error } = await POST('/texts', {
          body: model.value as TextCreate,
        });
        if (!error) {
          await loadPlatformData();
          state.text = createdText || state.text;
          router.push({ name: 'adminTextsSettings', params: { textSlug: createdText.slug } });
          message.success($t('admin.newText.msgSaveSuccess', { title: createdText.title }));
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
  <icon-heading level="1" :icon="AddCircleIcon">
    {{ $t('admin.newText.heading') }}
    <help-button-widget help-key="adminNewTextView" />
  </icon-heading>

  <n-alert :title="$t('general.info')" type="info" closable>
    {{ $t('admin.newText.headerInfoAlert') }}
  </n-alert>

  <div class="content-block">
    <n-form
      ref="formRef"
      :model="model"
      :rules="textFormRules"
      :disabled="loading"
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
          @keydown.enter.prevent
        />
      </n-form-item>

      <!-- STRUCTURE LEVELS -->
      <n-form-item :label="$t('models.text.level', 2)" path="levels" required>
        <n-dynamic-input
          v-model:value="model.levels"
          :min="1"
          :max="32"
          item-class="mb-0"
          @create="() => [{ locale: '*', translation: '' }]"
        >
          <template #default="{ index: levelIndex }">
            <div style="padding-right: 12px">{{ levelIndex + 1 }}.</div>
            <div style="flex-grow: 2">
              <!-- STRUCTURE LEVEL LABEL -->
              <n-form-item
                ignore-path-change
                :show-label="false"
                :path="`levels[${levelIndex}][0].translation`"
                :rule="textFormRules.levelTranslation"
                style="flex-grow: 2"
              >
                <n-input
                  v-model:value="model.levels[levelIndex][0].translation"
                  type="text"
                  :placeholder="$t('models.text.levelLabel')"
                  @keydown.enter.prevent
                />
              </n-form-item>
            </div>
          </template>
          <template #action="{ index, create, remove }">
            <dynamic-input-controls
              :movable="false"
              :remove-disabled="model.levels.length === 1"
              :insert-disabled="model.levels.length >= 32"
              @remove="() => remove(index)"
              @insert="() => create(index)"
            />
          </template>
        </n-dynamic-input>
      </n-form-item>
    </n-form>

    <button-shelf top-gap>
      <n-button type="primary" :disabled="loading" :loading="loading" @click="handleSave">
        {{ $t('general.saveAction') }}
      </n-button>
    </button-shelf>
  </div>
</template>
