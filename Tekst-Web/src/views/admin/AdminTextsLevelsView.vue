<script setup lang="ts">
import { useStateStore } from '@/stores';
import InsertLevelButton from '@/components/admin/InsertLevelButton.vue';
import { textFormRules } from '@/formRules';
import {
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
import type { StructureLevelTranslation } from '@/api';
import ButtonFooter from '@/components/ButtonFooter.vue';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import { negativeButtonProps, positiveButtonProps } from '@/components/dialogButtonProps';

import { useMessages } from '@/messages';
import { $t } from '@/i18n';
import { POST, PATCH, DELETE } from '@/api';
import { usePlatformData } from '@/platformData';
import { useI18n } from 'vue-i18n';

import AddRound from '@vicons/material/AddRound';
import MinusRound from '@vicons/material/MinusRound';
import DeleteRound from '@vicons/material/DeleteRound';
import EditRound from '@vicons/material/EditRound';

const state = useStateStore();
const { loadPlatformData } = usePlatformData();
const { message } = useMessages();
const { locale } = useI18n({ useScope: 'global' });
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
    ? $t('admin.text.levels.tipEditLevel', {
        levelLabel: getLevelLabel(levels.value[editModalLevel.value]),
      })
    : $t('admin.text.levels.tipInsertLevel', { n: editModalLevel.value + 1 })
);
const editModalWarning = computed(() =>
  editModalAction.value === 'edit' ? undefined : $t('admin.text.levels.warnInsertLevel')
);

const levelLocaleOptions = computed(() =>
  Object.keys(localeProfiles).map((l) => ({
    label: `${localeProfiles[l].icon} ${localeProfiles[l].displayFull}`,
    value: localeProfiles[l].key,
    disabled: !!formModel.value.translations
      .map((lvlTrans: StructureLevelTranslation) => lvlTrans.locale)
      .includes(l),
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
    title: $t('general.warning'),
    content: $t('admin.text.levels.warnDeleteLevel', {
      levelLabel: targetLevelLabel,
    }),
    positiveText: $t('general.deleteAction'),
    negativeText: $t('general.cancelAction'),
    positiveButtonProps,
    negativeButtonProps,
    autoFocus: false,
    closable: false,
    onPositiveClick: async () => {
      loading.value = true;
      const { data, error } = await DELETE('/texts/{id}/level/{index}', {
        params: { path: { id: state.text?.id || '', index: level } },
      });
      if (!error) {
        state.text = data;
        message.success(
          $t('admin.text.levels.msgDeleteSuccess', {
            levelLabel: targetLevelLabel,
          })
        );
      } else {
        message.error($t('errors.unexpected'), error);
      }
      loading.value = false;
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
    ?.validate(async (validationError) => {
      if (validationError) return;
      loading.value = true;

      if (editModalAction.value === 'insert') {
        const { data, error } = await POST('/texts/{id}/level/{index}', {
          params: { path: { id: state.text?.id || '', index: editModalLevel.value } },
          body: formModel.value.translations,
        });
        if (!error) {
          state.text = data;
          message.success(
            $t('admin.text.levels.msgInsertSuccess', { position: editModalLevel.value + 1 })
          );
        } else {
          message.error($t('errors.unexpected'), error);
        }
      } else if (editModalAction.value === 'edit') {
        const textUpdates = {
          levels: state.text?.levels.map((lvl, i) => {
            if (i === editModalLevel.value) {
              return formModel.value.translations;
            } else {
              return lvl;
            }
          }),
        };
        const { data, error } = await PATCH('/texts/{id}', {
          params: { path: { id: state.text?.id || '' } },
          body: textUpdates,
        });
        if (!error) {
          state.text = data;
          message.success(
            $t('admin.text.levels.msgEditSuccess', { position: editModalLevel.value + 1 })
          );
        } else {
          message.error($t('errors.unexpected'), error);
        }
      }
      await loadPlatformData();
      loading.value = false;
      showEditModal.value = false;
    })
    .catch(() => {
      message.error($t('errors.followFormRules'));
    });
}
</script>

<template>
  <h2>
    {{ $t('admin.text.levels.heading') }}
    <HelpButtonWidget help-key="adminTextsLevelsView" />
  </h2>

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
            :title="$t('admin.text.levels.tipEditLevel', { levelLabel: getLevelLabel(lvl) })"
            :focusable="false"
            @click="() => handleEditClick(lvlIndex)"
          >
            <n-icon :component="EditRound" />
          </n-button>
          <n-button
            secondary
            circle
            :title="$t('admin.text.levels.tipDeleteLevel', { levelLabel: getLevelLabel(lvl) })"
            :focusable="false"
            @click="() => handleDeleteClick(lvlIndex)"
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
    :auto-focus="false"
    size="large"
    class="tekst-modal"
    to="#app-container"
    @after-leave="destroyEditModal"
  >
    <h2>{{ editModalTitle }}</h2>

    <n-alert
      v-if="editModalWarning"
      closable
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
      <n-form-item ignore-path-change :show-label="false" path="translations">
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
                  :disabled="loading"
                  style="min-width: 200px; font-weight: var(--app-ui-font-weight-normal)"
                  @keydown.enter.prevent
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
                  :disabled="loading"
                  @keydown.enter.prevent
                />
              </n-form-item>
            </div>
          </template>
          <template #action="{ index: indexAction, create, remove }">
            <ButtonFooter>
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
            </ButtonFooter>
          </template>
        </n-dynamic-input>
      </n-form-item>
    </n-form>

    <ButtonFooter>
      <n-button secondary :disabled="loading" @click="showEditModal = false">
        {{ $t('general.cancelAction') }}
      </n-button>
      <n-button type="primary" :loading="loading" :disabled="loading" @click="handleModalSubmit">
        {{ $t('general.saveAction') }}
      </n-button>
    </ButtonFooter>
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
