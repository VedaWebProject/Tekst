<script setup lang="ts">
import type { Translation } from '@/api';
import { DELETE, PATCH, POST } from '@/api';
import { dialogProps } from '@/common';
import FormSectionHeading from '@/components/FormSectionHeading.vue';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import GenericModal from '@/components/generic/GenericModal.vue';
import InsertItemSeparator from '@/components/InsertItemSeparator.vue';
import { useMessages } from '@/composables/messages';
import { usePlatformData } from '@/composables/platformData';
import { textFormRules } from '@/forms/formRules';
import TranslationFormItem from '@/forms/TranslationFormItem.vue';
import { $t, getLocaleProfile } from '@/i18n';
import { DeleteIcon, EditIcon } from '@/icons';
import { useStateStore } from '@/stores';
import { NAlert, NButton, NFlex, NForm, NIcon, useDialog, type FormInst } from 'naive-ui';
import { computed, ref } from 'vue';

const state = useStateStore();
const { loadPlatformData } = usePlatformData();
const { message } = useMessages();
const dialog = useDialog();

const levels = computed<Translation[][]>(() => state.text?.levels || [[]]);

const showEditModal = ref(false);
const formModel = ref<{ translations: Translation[] }>({ translations: [] });
const formRef = ref<FormInst | null>(null);
const loading = ref(false);
const editModalLevel = ref<number>(-1);
const editModalAction = ref<'edit' | 'insert'>('edit');
const editModalTitle = computed(() =>
  editModalAction.value === 'edit'
    ? $t('texts.levels.tipEditLevel', {
        levelLabel: getLevelLabel(levels.value[editModalLevel.value]),
      })
    : $t('texts.levels.tipInsertLevel', { n: editModalLevel.value + 1 })
);
const editModalWarning = computed(() =>
  editModalAction.value === 'edit' ? undefined : $t('texts.levels.warnInsertLevel')
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
    title: $t('common.warning'),
    content: $t('texts.levels.warnDeleteLevel', {
      levelLabel: targetLevelLabel,
    }),
    positiveText: $t('common.delete'),
    negativeText: $t('common.cancel'),
    closable: false,
    ...dialogProps,
    onPositiveClick: async () => {
      loading.value = true;
      const { data, error } = await DELETE('/texts/{id}/level/{lvl}', {
        params: { path: { id: state.text?.id || '', lvl: level } },
      });
      if (!error) {
        loadPlatformData();
        state.text = data;
        message.success(
          $t('texts.levels.msgDeleteSuccess', {
            levelLabel: targetLevelLabel,
          })
        );
      }
      loading.value = false;
    },
  });
}

function getLevelLabel(lvl: Translation[]) {
  if (!lvl?.length) return '';
  return lvl.find((t) => t.locale === state.locale)?.translation || lvl[0].translation || '';
}

function destroyEditModal() {
  formModel.value.translations = [];
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
          loadPlatformData();
          state.text = data;
          message.success(
            $t('texts.levels.msgInsertSuccess', { position: editModalLevel.value + 1 })
          );
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
          loadPlatformData();
          state.text = data;
          message.success(
            $t('texts.levels.msgEditSuccess', { position: editModalLevel.value + 1 })
          );
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
  <div>
    <form-section-heading :label="$t('common.level', 2)" help-key="textLevels" />

    <div v-for="(lvl, lvlIndex) in levels" :key="`lvl_${lvlIndex}`">
      <insert-item-separator
        :title="$t('texts.levels.tipInsertLevel', { n: lvlIndex + 1 })"
        :disabled="levels.length >= 32"
        @click="() => handleInsertClick(lvlIndex)"
      />
      <n-flex align="center" :wrap="false" class="level">
        <div class="level-index">{{ lvlIndex + 1 }}.</div>
        <n-flex vertical :wrap="false" style="flex: 2">
          <n-flex v-for="lvlTranslation in lvl" :key="lvlTranslation.locale" :wrap="false">
            <span>{{ getLocaleProfile(lvlTranslation.locale)?.icon || '🌐' }}</span>
            <span>{{ lvlTranslation.translation }}</span>
          </n-flex>
        </n-flex>
        <div class="level-buttons">
          <n-button
            secondary
            circle
            :title="$t('texts.levels.tipEditLevel', { levelLabel: getLevelLabel(lvl) })"
            :focusable="false"
            @click="() => handleEditClick(lvlIndex)"
          >
            <n-icon :component="EditIcon" />
          </n-button>
          <n-button
            secondary
            circle
            :title="$t('texts.levels.tipDeleteLevel', { levelLabel: getLevelLabel(lvl) })"
            :focusable="false"
            @click="() => handleDeleteClick(lvlIndex)"
          >
            <n-icon :component="DeleteIcon" />
          </n-button>
        </div>
      </n-flex>
    </div>

    <insert-item-separator
      :title="$t('texts.levels.tipInsertLevel', { n: levels.length + 1 })"
      :disabled="levels.length >= 32"
      @click="() => handleInsertClick(levels.length)"
    />

    <generic-modal
      v-model:show="showEditModal"
      :title="editModalTitle"
      :icon="EditIcon"
      @after-leave="destroyEditModal"
    >
      <n-alert
        v-if="editModalWarning"
        closable
        :title="$t('common.warning')"
        type="warning"
        class="mb-lg"
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
        <translation-form-item
          v-model="formModel.translations"
          parent-form-path-prefix="translations"
          :loading="loading"
          :main-form-label="$t('common.level')"
          :translation-form-label="$t('common.level')"
          :translation-form-rules="textFormRules.levelTranslation"
        />
      </n-form>

      <button-shelf top-gap>
        <n-button secondary :disabled="loading" @click="showEditModal = false">
          {{ $t('common.cancel') }}
        </n-button>
        <n-button type="primary" :loading="loading" :disabled="loading" @click="handleModalSubmit">
          {{ $t('common.save') }}
        </n-button>
      </button-shelf>
    </generic-modal>
  </div>
</template>

<style scoped>
.level:not(:last-child) {
  margin-bottom: var(--gap-md);
}

.level-index {
  min-width: 28px;
  align-self: stretch;
  color: var(--accent-color);
  font-weight: var(--font-weight-bold);
  border-right: 2px solid var(--accent-color);
}

.level-buttons {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 12px;
}
</style>
