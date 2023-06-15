<script setup lang="ts">
import { useStateStore } from '@/stores';
import InsertLevelButton from '@/components/admin/InsertLevelButton.vue';
import { useFormRules } from '@/formRules';
import {
  NSpace,
  NIcon,
  NInput,
  NSelect,
  NModal,
  NAlert,
  NButton,
  NForm,
  NFormItem,
  NDynamicInput,
  type FormInst,
  useDialog,
} from 'naive-ui';
import { computed, ref } from 'vue';
import { localeProfiles } from '@/i18n';
import type { StructureLevelTranslation, StructureLevelTranslationLocaleEnum } from '@/openapi';

import AddRound from '@vicons/material/AddRound';
import MinusRound from '@vicons/material/MinusRound';

import DeleteRound from '@vicons/material/DeleteRound';
import EditRound from '@vicons/material/EditRound';
import { useMessages } from '@/messages';
import { useI18n } from 'vue-i18n';
import { useApi } from '@/api';
import { usePlatformData } from '@/platformData';

const state = useStateStore();
const { loadPlatformData } = usePlatformData();
const { message } = useMessages();
const { textsApi } = useApi();
const { locale } = useI18n();
const { textFormRules } = useFormRules();
const { t } = useI18n({ useScope: 'global' });
const dialog = useDialog();

const levels = computed<StructureLevelTranslation[][]>(() => state.text?.levels || [[]]);

const showEditModal = ref(false);
const formModel = ref<Record<string, any>>({});
const formRef = ref<FormInst | null>(null);
const loading = ref(false);
const editModalLevel = ref<number>(-1);
const editModalAction = ref<'edit' | 'insert'>('edit');
const editModalTitle = computed(() =>
  editModalAction.value === 'edit'
    ? t('admin.texts.levels.tipEditLevel', {
        levelLabel: getLevelLabel(levels.value[editModalLevel.value]),
      })
    : t('admin.texts.levels.tipInsertLevel', { n: editModalLevel.value + 1 })
);
const editModalWarning = computed(() =>
  editModalAction.value === 'edit' ? undefined : t('admin.texts.levels.warnInsertLevel')
);

const levelLocaleOptions = computed(() =>
  Object.keys(localeProfiles).map((l) => ({
    label: `${localeProfiles[l].icon} ${localeProfiles[l].displayFull}`,
    value: localeProfiles[l].apiLocaleEnum,
    disabled: !!formModel.value.translations
      .map((lvlTrans: StructureLevelTranslation) => lvlTrans.locale)
      .includes(l as StructureLevelTranslationLocaleEnum),
  }))
);

function handleInsertClick(level: number) {
  formModel.value = { translations: [{ locale: null, label: null }] };
  editModalAction.value = 'insert';
  editModalLevel.value = level;
  showEditModal.value = true;
}

function handleEditClick(level: number) {
  formModel.value = {
    translations: levels.value[level].map((l) => ({ locale: l.locale, label: l.label })),
  };
  editModalAction.value = 'edit';
  editModalLevel.value = level;
  showEditModal.value = true;
}

function handleDeleteClick(level: number) {
  const targetLevelLabel = getLevelLabel(levels.value[level]);
  dialog.warning({
    title: t('general.warning'),
    content: t('admin.texts.levels.warnDeleteLevel', {
      levelLabel: targetLevelLabel,
    }),
    positiveText: t('general.deleteAction'),
    negativeText: t('general.cancelAction'),
    style: 'font-weight: var(--app-ui-font-weight-light); width: 680px; max-width: 95%',
    onPositiveClick: async () => {
      loading.value = true;
      try {
        state.text = (
          await textsApi.deleteLevel({
            id: state.text?.id || '',
            index: level,
          })
        ).data;
        message.success(
          t('admin.texts.levels.msgDeleteSuccess', {
            levelLabel: targetLevelLabel,
          })
        );
        await loadPlatformData();
      } catch {
        message.error(t('errors.unexpected'));
      } finally {
        loading.value = false;
      }
    },
  });
}

function getLevelLabel(lvl: StructureLevelTranslation[]) {
  return (lvl && lvl.find((t) => t.locale === locale.value)?.label) || lvl[0]?.label || '';
}

function destroyEditModal() {
  formModel.value = {};
  editModalAction.value = 'edit';
  editModalLevel.value = -1;
}

async function handleModalSubmit() {
  formRef.value
    ?.validate(async (errors) => {
      if (!errors) {
        loading.value = true;
        try {
          if (editModalAction.value === 'insert') {
            state.text = (
              await textsApi.insertLevel({
                id: state.text?.id || '',
                index: editModalLevel.value,
                structureLevelTranslation: formModel.value.translations,
              })
            ).data;
            message.success(
              t('admin.texts.levels.msgInsertSuccess', { position: editModalLevel.value + 1 })
            );
          } else if (editModalAction.value === 'edit') {
            state.text = (
              await textsApi.updateText({
                id: state.text?.id || '',
                textUpdate: {
                  levels: state.text?.levels.map((lvl, i) => {
                    if (i === editModalLevel.value) {
                      return formModel.value.translations;
                    } else {
                      return lvl;
                    }
                  }),
                },
              })
            ).data;
            message.success(
              t('admin.texts.levels.msgEditSuccess', { position: editModalLevel.value + 1 })
            );
          }
          await loadPlatformData();
        } catch {
          message.error(t('errors.unexpected'));
        } finally {
          loading.value = false;
          showEditModal.value = false;
        }
      }
    })
    .catch(() => {
      message.error(t('errors.followFormRules'));
    });
}
</script>

<template>
  <h1>
    {{ $t('admin.heading') }}: {{ state.text?.title }} - {{ $t('admin.texts.levels.heading') }}
  </h1>

  <div class="content-block">
    <div v-for="(lvl, lvlIndex) in levels" :key="`lvl_${lvlIndex}`">
      <insert-level-button :level="lvlIndex" @click="handleInsertClick" />
      <div class="level">
        <div class="level-index">{{ lvlIndex + 1 }}.</div>
        <div class="level-translations">
          <template v-for="lvlTranslation in lvl" :key="lvlTranslation.locale">
            <div>
              {{ localeProfiles[lvlTranslation.locale].icon }}
              <span style="font-weight: normal">
                {{ localeProfiles[lvlTranslation.locale].displayFull }}:
              </span>
            </div>
            <div>
              {{ lvlTranslation.label }}
            </div>
          </template>
        </div>
        <div class="level-buttons">
          <n-button
            secondary
            circle
            :title="$t('admin.texts.levels.tipEditLevel', { levelLabel: getLevelLabel(lvl) })"
            @click="() => handleEditClick(lvlIndex)"
            :focusable="false"
          >
            <n-icon :component="EditRound" />
          </n-button>
          <n-button
            secondary
            circle
            :title="$t('admin.texts.levels.tipDeleteLevel', { levelLabel: getLevelLabel(lvl) })"
            @click="() => handleDeleteClick(lvlIndex)"
            :focusable="false"
          >
            <n-icon :component="DeleteRound" />
          </n-button>
        </div>
      </div>
    </div>

    <insert-level-button :level="levels.length" @click="handleInsertClick" />
  </div>

  <n-modal
    v-model:show="showEditModal"
    preset="card"
    embedded
    :closable="false"
    size="large"
    class="tekst-modal"
    to="#app-container"
    @after-leave="destroyEditModal"
  >
    <h2>{{ editModalTitle }}</h2>

    <n-alert
      v-if="editModalWarning"
      :title="$t('general.warning')"
      type="warning"
      style="margin-bottom: 1rem"
    >
      {{ editModalWarning }}
    </n-alert>

    <n-form
      ref="formRef"
      :model="formModel"
      :rules="textFormRules"
      label-placement="top"
      label-width="auto"
      require-mark-placement="right-hanging"
    >
      <!-- STRUCTURE LEVEL -->
      <n-form-item ignore-path-change :show-label="false" :path="`translations`">
        <n-dynamic-input
          v-model:value="formModel.translations"
          :min="1"
          :max="Object.keys(localeProfiles).length"
          item-style="margin-bottom: 0;"
          :disabled="loading"
          @create="() => ({ locale: null, label: '' })"
        >
          <template #default="{ index: translationIndex }">
            <div style="display: flex; align-items: flex-start; gap: 12px; width: 100%">
              <!-- STRUCTURE LEVEL LOCALE -->
              <n-form-item
                ignore-path-change
                :show-label="false"
                :path="`translations[${translationIndex}].locale`"
                :rule="textFormRules.levelTranslationLocale"
              >
                <n-select
                  v-model:value="formModel.translations[translationIndex].locale"
                  :options="levelLocaleOptions"
                  :placeholder="$t('general.language')"
                  :consistent-menu-width="false"
                  @keydown.enter.prevent
                  :disabled="loading"
                  style="min-width: 200px; font-weight: var(--app-ui-font-weight-normal)"
                />
              </n-form-item>
              <!-- STRUCTURE LEVEL LABEL -->
              <n-form-item
                ignore-path-change
                :show-label="false"
                :path="`translations[${translationIndex}].label`"
                :rule="textFormRules.levelTranslationLabel"
                style="flex-grow: 2"
              >
                <n-input
                  v-model:value="formModel.translations[translationIndex].label"
                  type="text"
                  :placeholder="$t('models.text.levelLabel')"
                  @keydown.enter.prevent
                  :disabled="loading"
                />
              </n-form-item>
            </div>
          </template>
          <template #action="{ index: indexAction, create, remove }">
            <n-space style="margin-left: 20px; flex-wrap: nowrap">
              <n-button
                secondary
                circle
                :disabled="formModel.translations.length === 1"
                @click="() => remove(indexAction)"
              >
                <template #icon>
                  <n-icon :component="MinusRound" />
                </template>
              </n-button>
              <n-button
                secondary
                circle
                :disabled="formModel.translations.length >= Object.keys(localeProfiles).length"
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
    </n-form>

    <n-space :size="12" justify="end" style="margin-top: 0.5rem">
      <n-button
        secondary
        block
        @click="showEditModal = false"
        :loading="loading"
        :disabled="loading"
      >
        {{ $t('general.cancelAction') }}
      </n-button>
      <n-button
        block
        type="primary"
        @click="handleModalSubmit"
        :loading="loading"
        :disabled="loading"
      >
        {{ $t('general.saveAction') }}
      </n-button>
    </n-space>
  </n-modal>
</template>

<style scoped>
.level {
  display: flex;
  gap: 12px;
  align-items: center;
}

.level:not(:last-child) {
  margin-bottom: 0.75rem;
}

.level-index {
  min-width: 28px;
  color: var(--accent-color);
  font-weight: bold;
}

.level-translations {
  display: grid;
  grid-template-columns: auto 1fr;
  flex-grow: 2;
}

.level-translations > * {
  padding-right: 28px;
  white-space: nowrap;
  overflow-x: hidden;
  text-overflow: ellipsis;
}

.level-buttons {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 12px;
}
</style>
