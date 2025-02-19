<script setup lang="ts">
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import { $t } from '@/i18n';

import { DELETE, GET, type IndexInfoResponse, type TaskRead } from '@/api';
import FormSectionHeading from '@/components/FormSectionHeading.vue';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import { useMessages } from '@/composables/messages';
import { useTasks } from '@/composables/tasks';
import { DeleteIcon, MaintenanceIcon, RefreshIcon, UpdateIcon } from '@/icons';
import { useStateStore, useThemeStore } from '@/stores';
import { utcToLocalTime } from '@/utils';
import {
  NAlert,
  NButton,
  NIcon,
  NTable,
  NTabPane,
  NTabs,
  NTime,
  useThemeVars,
  type TabsInst,
} from 'naive-ui';
import { onBeforeMount, ref, watch } from 'vue';
import { RouterLink } from 'vue-router';

const state = useStateStore();
const theme = useThemeStore();
const nuiTheme = useThemeVars();
const { message } = useMessages();
const { addTask, startTasksPolling } = useTasks();

const tabsRef = ref<TabsInst>();
const allTasks = ref<TaskRead[]>([]);
const indicesInfo = ref<IndexInfoResponse>();
const indicesInfoLoading = ref(false);
const precomputedLoading = ref(false);
const tasksLoading = ref(false);

const statusColors: Record<string, string> = {
  waiting: 'inherit',
  running: nuiTheme.value.infoColor,
  done: nuiTheme.value.successColor,
  failed: nuiTheme.value.errorColor,
};

async function createIndex() {
  indicesInfoLoading.value = true;
  const { data, error } = await GET('/search/index/create');
  if (!error) {
    addTask(data);
    message.info($t('admin.maintenance.indices.actionCreateStarted'));
    startTasksPolling();
  }
  indicesInfoLoading.value = false;
}

async function triggerPrecomputation() {
  precomputedLoading.value = true;
  const { data, error } = await GET('/resources/maintenance');
  if (!error) {
    addTask(data);
    message.info($t('admin.maintenance.precomputed.actionStarted'));
    startTasksPolling();
  }
  precomputedLoading.value = false;
}

async function deleteTask(id: string) {
  tasksLoading.value = true;
  const { error } = await DELETE('/platform/tasks/{id}', { params: { path: { id } } });
  if (!error) {
    allTasks.value = allTasks.value.filter((task) => task.id !== id);
  }
  tasksLoading.value = false;
}

async function deleteAllTasks() {
  tasksLoading.value = true;
  const { error } = await DELETE('/platform/tasks');
  if (!error) {
    message.success($t('admin.maintenance.tasks.actionDeleteAllSuccess'));
    allTasks.value = [];
  }
  tasksLoading.value = false;
}

async function updateAllTasksData() {
  tasksLoading.value = true;
  const { data, error } = await GET('/platform/tasks');
  if (!error) {
    allTasks.value = data.sort(
      (a, b) =>
        (b.startTime ? Date.parse(b.startTime) : 0) - (a.startTime ? Date.parse(a.startTime) : 0)
    );
  }
  tasksLoading.value = false;
}

async function loadIndexInfo() {
  indicesInfoLoading.value = true;
  const { data, error } = await GET('/search/index/info');
  if (!error) {
    indicesInfo.value = data;
  }
  indicesInfoLoading.value = false;
}

function getFieldMappingsStatus(fields: number) {
  const maxFieldMappings = state.pf?.maxFieldMappings || 0;
  if (fields > maxFieldMappings * 0.9) {
    return 'over';
  } else if (fields > maxFieldMappings * 0.75) {
    return 'near';
  } else {
    return 'ok';
  }
}

watch(
  () => state.locale,
  () => {
    setTimeout(() => {
      tabsRef.value?.syncBarPosition();
    }, 100);
  }
);

onBeforeMount(() => {
  loadIndexInfo();
  updateAllTasksData();
});
</script>

<template>
  <icon-heading level="1" :icon="MaintenanceIcon">
    {{ $t('admin.maintenance.heading') }}
    <help-button-widget help-key="adminMaintenanceView" />
  </icon-heading>

  <div class="content-block">
    <n-tabs
      ref="tabsRef"
      type="line"
      :placement="state.smallScreen ? 'top' : 'left'"
      :pane-class="state.smallScreen ? 'mt-md' : 'ml-lg'"
    >
      <!-- SEARCH INDICES -->
      <n-tab-pane :tab="$t('admin.maintenance.indices.heading')" name="1">
        <form-section-heading :label="$t('admin.maintenance.indices.heading')" />
        <button-shelf bottom-gap>
          <template #start>
            <n-button
              secondary
              :disabled="indicesInfoLoading"
              :loading="indicesInfoLoading"
              @click="loadIndexInfo"
            >
              <template #icon>
                <n-icon :component="RefreshIcon" />
              </template>
              {{ $t('general.refreshAction') }}
            </n-button>
            <n-button secondary :disabled="indicesInfoLoading" @click="createIndex">
              <template #icon>
                <n-icon :component="UpdateIcon" />
              </template>
              {{ $t('admin.maintenance.indices.actionCreate') }}
            </n-button>
          </template>
        </button-shelf>

        <n-table
          v-for="(indexInfo, i) in indicesInfo"
          :key="`${i}_${indexInfo.textId}`"
          size="small"
          style="table-layout: fixed"
          :bordered="false"
          class="mb-lg"
        >
          <thead>
            <tr>
              <th
                colspan="2"
                :style="{
                  backgroundColor: theme.getAccentColors(indexInfo.textId).fade4,
                }"
              >
                {{ state.textById(indexInfo.textId)?.title || '???' }}
              </th>
            </tr>
          </thead>
          <tbody>
            <template v-for="(value, key) in indexInfo" :key="key">
              <tr v-if="!['textId', 'fields', 'upToDate'].includes(key)">
                <th style="font-weight: var(--font-weight-normal)">
                  {{ $t(`admin.maintenance.indices.${key}`) }}
                </th>
                <td>{{ value }}</td>
              </tr>
            </template>
            <tr>
              <th style="font-weight: var(--font-weight-normal)">
                {{ $t(`admin.maintenance.indices.fields`) }}
              </th>
              <td :class="`max-fields-warn-${getFieldMappingsStatus(indexInfo.fields)}`">
                {{ indexInfo.fields }} / {{ state.pf?.maxFieldMappings || '???' }}
              </td>
            </tr>
            <tr>
              <th style="font-weight: var(--font-weight-normal)">
                {{ $t(`general.status`) }}
              </th>
              <td>
                <span
                  :class="{ 'index-ood': !indexInfo.upToDate, 'index-utd': indexInfo.upToDate }"
                  >{{
                    indexInfo.upToDate
                      ? $t('admin.maintenance.indices.utd')
                      : $t('admin.maintenance.indices.ood')
                  }}</span
                >
              </td>
            </tr>
          </tbody>
        </n-table>
      </n-tab-pane>

      <!-- PRECOMPUTED DATA ON RESOURCES -->
      <n-tab-pane :tab="$t('admin.maintenance.precomputed.heading')" name="2">
        <form-section-heading :label="$t('admin.maintenance.precomputed.heading')" />
        <button-shelf bottom-gap>
          <template #start>
            <n-button
              secondary
              :disabled="precomputedLoading"
              :loading="precomputedLoading"
              @click="triggerPrecomputation"
            >
              <template #icon>
                <n-icon :component="UpdateIcon" />
              </template>
              {{ $t('general.precomputeAction') }}
            </n-button>
          </template>
        </button-shelf>
        <n-alert type="info" :title="$t('general.info')">
          {{ $t('admin.maintenance.precomputed.description') }}
        </n-alert>
      </n-tab-pane>

      <!-- SYSTEM BACKGROUND TASKS -->
      <n-tab-pane :tab="$t('tasks.title')" name="3">
        <form-section-heading :label="$t('tasks.title')" />
        <button-shelf bottom-gap>
          <template #start>
            <n-button
              secondary
              :disabled="tasksLoading"
              :loading="tasksLoading"
              @click="updateAllTasksData"
            >
              <template #icon>
                <n-icon :component="RefreshIcon" />
              </template>
              {{ $t('general.refreshAction') }}
            </n-button>
            <n-button
              secondary
              type="error"
              :disabled="tasksLoading"
              :loading="tasksLoading"
              @click="deleteAllTasks"
            >
              <template #icon>
                <n-icon :component="DeleteIcon" />
              </template>
              {{ $t('admin.maintenance.tasks.actionDeleteAll') }}
            </n-button>
          </template>
        </button-shelf>

        <n-table size="small" style="table-layout: fixed">
          <thead>
            <tr>
              <th>{{ $t('general.type') }}</th>
              <th>{{ $t('general.status') }}</th>
              <th>{{ $t('admin.maintenance.tasks.started') }}</th>
              <th>{{ $t('admin.maintenance.tasks.ended') }}</th>
              <th>{{ $t('admin.maintenance.tasks.duration') }}</th>
              <th>{{ $t('admin.maintenance.tasks.startedBy') }}</th>
              <th></th>
            </tr>
          </thead>
          <tbody v-if="allTasks.length">
            <tr v-for="task in allTasks" :key="task.id">
              <td>{{ $t(`tasks.types.${task.type}`) }}</td>
              <td class="nowrap" :style="{ color: statusColors[task.status || 'running'] }">
                {{ $t(`tasks.statuses.${task.status}`) }}
              </td>
              <td class="nowrap">
                <n-time
                  v-if="task.startTime"
                  :time="utcToLocalTime(task.startTime)"
                  type="datetime"
                />
                <span v-else>–</span>
              </td>
              <td class="nowrap">
                <n-time v-if="task.endTime" :time="utcToLocalTime(task.endTime)" type="datetime" />
                <span v-else>–</span>
              </td>
              <td class="nowrap">
                {{
                  task.durationSeconds
                    ? $t('admin.maintenance.tasks.seconds', {
                        seconds: task.durationSeconds.toFixed(2),
                      })
                    : '–'
                }}
              </td>
              <td class="nowrap">
                <router-link
                  v-if="task.userId"
                  :to="{ name: 'user', params: { username: task.userId } }"
                >
                  {{ $t('models.user.modelLabel') }}
                </router-link>
                <span v-else>
                  {{ $t('general.system') }}
                </span>
              </td>
              <td class="nowrap">
                <n-button
                  secondary
                  size="small"
                  :title="$t('general.deleteAction')"
                  :disabled="tasksLoading"
                  :loading="tasksLoading"
                  @click="deleteTask(task.id)"
                >
                  <template #icon>
                    <n-icon :component="DeleteIcon" />
                  </template>
                </n-button>
              </td>
            </tr>
          </tbody>

          <tbody v-else>
            <tr>
              <td colspan="999">
                {{ $t('admin.maintenance.tasks.noTasks') }}
              </td>
            </tr>
          </tbody>
        </n-table>
      </n-tab-pane>
    </n-tabs>
  </div>
</template>

<style scoped>
.content-block :deep(table.n-table) {
  max-width: 100%;
}

.content-block :deep(table.n-table) {
  table-layout: auto !important;
}

.content-block :deep(.n-table),
.content-block :deep(.n-table td) {
  background-color: transparent;
}

.content-block :deep(.n-table td.nowrap) {
  white-space: nowrap;
}

.max-fields-warn-near {
  color: v-bind('nuiTheme.warningColor');
  font-weight: var(--font-weight-bold);
}

.max-fields-warn-over {
  color: v-bind('nuiTheme.errorColor');
  font-weight: var(--font-weight-bold);
}

.index-ood {
  color: v-bind('nuiTheme.errorColor');
  font-weight: var(--font-weight-bold);
}

.index-utd {
  color: v-bind('nuiTheme.successColor');
}
</style>
