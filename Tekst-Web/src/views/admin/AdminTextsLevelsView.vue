<script setup lang="ts">
import { useStateStore } from '@/stores';
import InsertLevelButton from '@/components/admin/InsertLevelButton.vue';
import { textFormRules } from '@/forms/formRules';
import { NIcon, NAlert, NButton, NForm, type FormInst, useDialog } from 'naive-ui';
import { computed, ref } from 'vue';
import { getLocaleProfile } from '@/i18n';
import type { Translation } from '@/api';
import ButtonShelf from '@/components/ButtonShelf.vue';
import HelpButtonWidget from '@/components/widgets/HelpButtonWidget.vue';
import { negativeButtonProps, positiveButtonProps } from '@/components/dialogButtonProps';
import { useMessages } from '@/messages';
import { $t } from '@/i18n';
import { POST, PATCH, DELETE } from '@/api';
import { usePlatformData } from '@/platformData';
import { useI18n } from 'vue-i18n';
import TranslationFormItem from '@/forms/TranslationFormItem.vue';
import GenericModal from '@/components/GenericModal.vue';

import DeleteRound from '@vicons/material/DeleteRound';
import EditRound from '@vicons/material/EditRound';

const state = useStateStore();
const { loadPlatformData } = usePlatformData();
const { message } = useMessages();
const { locale } = useI18n({ useScope: 'global' });
const dialog = useDialog();

const levels = computed<Translation[][]>(() => state.text?.levels || [[]]);

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

function handleInsertClick(level: number) {
  formModel.value = { translations: [{ locale: '*', translation: '' }] };
  editModalAction.value = 'insert';
  editModalLevel.value = level;
  showEditModal.value = true;
}

function handleEditClick(level: number) {
  formModel.value = {
    translations: levels.value[level].map((l) => ({
      locale: l.locale,
      translation: l.translation,
    })),
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

function getLevelLabel(lvl: Translation[]) {
  if (!lvl?.length) return '';
  return lvl.find((t) => t.locale === locale.value)?.translation || lvl[0].translation || '';
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
              {{ getLocaleProfile(lvlTranslation.locale)?.icon || '🌐' }}
              <span style="font-weight: normal">
                {{
                  getLocaleProfile(lvlTranslation.locale)?.displayFull ||
                  $t('models.locale.allLanguages')
                }}:
              </span>
            </div>
            <div>
              {{ lvlTranslation.translation }}
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

  <GenericModal
    v-model:show="showEditModal"
    :title="editModalTitle"
    :icon="EditRound"
    @after-leave="destroyEditModal"
  >
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
      :disabled="loading"
      label-placement="top"
      label-width="auto"
      require-mark-placement="right-hanging"
    >
      <!-- STRUCTURE LEVEL -->
      <TranslationFormItem
        v-model:value="formModel.translations"
        parent-form-path-prefix="translations"
        :loading="loading"
        :main-form-label="$t('models.text.level')"
        :translation-form-label="$t('models.text.level')"
        :translation-form-rule="textFormRules.levelTranslation"
      />
    </n-form>

    <ButtonShelf top-gap>
      <n-button secondary :disabled="loading" @click="showEditModal = false">
        {{ $t('general.cancelAction') }}
      </n-button>
      <n-button type="primary" :loading="loading" :disabled="loading" @click="handleModalSubmit">
        {{ $t('general.saveAction') }}
      </n-button>
    </ButtonShelf>
  </GenericModal>
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
