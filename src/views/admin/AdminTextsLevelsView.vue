<script setup lang="ts">
import type { StructureLevelTranslation } from '@/openapi';
import { useStateStore } from '@/stores';
import { localeProfiles } from '@/i18n';
import { NButton, NIcon } from 'naive-ui';
import { computed } from 'vue';

import DeleteRound from '@vicons/material/DeleteRound';
import EditRound from '@vicons/material/EditRound';
import AddRound from '@vicons/material/AddRound';
import { useMessages } from '@/messages';
import { useI18n } from 'vue-i18n';

const state = useStateStore();
const { message } = useMessages();
const { locale } = useI18n();

const levels = computed<StructureLevelTranslation[][]>(() => state.text?.levels || [[]]);

function handleAddClick(level: number) {
  message.info(`INSERT: ${level}`);
}

function handleEditClick(level: number) {
  message.info(`EDIT: ${level}`);
}

function handleDeleteClick(level: number) {
  message.info(`DELETE: ${level}`);
}

function getLevelLabel(lvl: StructureLevelTranslation[]) {
  return lvl.find((t) => t.locale === locale.value)?.label;
}
</script>

<template>
  <div v-for="(lvl, lvlIndex) in levels" :key="`lvl_${lvlIndex}`">
    <div class="add-level-wrapper">
      <div class="add-level-separator"></div>
      <n-button
        dashed
        circle
        size="small"
        :title="$t('admin.texts.levels.tipAddLevel', { n: lvlIndex + 1 })"
        @click="() => handleAddClick(lvlIndex)"
      >
        <template #icon>
          <n-icon :component="AddRound" />
        </template>
      </n-button>
      <div class="add-level-separator"></div>
    </div>
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
        >
          <n-icon :component="EditRound" />
        </n-button>
        <n-button
          secondary
          circle
          :title="$t('admin.texts.levels.tipDeleteLevel', { levelLabel: getLevelLabel(lvl) })"
          @click="() => handleDeleteClick(lvlIndex)"
        >
          <n-icon :component="DeleteRound" />
        </n-button>
      </div>
    </div>
  </div>
  <div class="add-level-wrapper">
    <div class="add-level-separator"></div>
    <n-button
      dashed
      circle
      size="small"
      :title="$t('admin.texts.levels.tipAddLevel', { n: levels.length + 1 })"
      @click="() => handleAddClick(levels.length)"
    >
      <template #icon>
        <n-icon :component="AddRound" />
      </template>
    </n-button>
    <div class="add-level-separator"></div>
  </div>
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

.add-level-wrapper {
  display: flex;
  align-items: center;
  padding: 6px 0;
  text-align: center;
}

.add-level-separator {
  flex-grow: 2;
  height: 0;
  border-bottom: 1px dashed #888;
  opacity: 0.25;
}
</style>
