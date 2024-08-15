<script setup lang="ts">
import { $t } from '@/i18n';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';

import IconHeading from '@/components/generic/IconHeading.vue';
import { RefreshIcon, DeleteIcon, MaintenanceIcon, UpdateIcon } from '@/icons';
import { NTime, NFlex, NButton, NIcon, NTable } from 'naive-ui';
import { DELETE, GET, type IndexInfoResponse, type TaskRead } from '@/api';
import { useMessages } from '@/composables/messages';
import { onBeforeMount, ref } from 'vue';
import { useTasks } from '@/composables/tasks';
import { utcToLocalTime } from '@/utils';
import { usePlatformData } from '@/composables/platformData';
import { useThemeStore } from '@/stores';
import { RouterLink } from 'vue-router';

const { pfData } = usePlatformData();
const theme = useThemeStore();
const { message } = useMessages();
const { addTask, startTasksPolling } = useTasks();

const allTasks = ref<TaskRead[]>([]);
const indicesInfo = ref<IndexInfoResponse>();
const indicesInfoLoading = ref(false);
const resourceMaintenanceLoading = ref(false);
const tasksLoading = ref(false);

const statusColors: Record<string, string> = {
  waiting: 'inherit',
  running: 'var(--col-info)',
  done: 'var(--col-success)',
  failed: 'var(--col-error)',
};

async function createIndex() {
  indicesInfoLoading.value = true;
  const { data, error } = await GET('/search/index/create');
  if (!error) {
    addTask(data);
    message.info($t('admin.system.maintenance.indices.actionCreateStarted'));
    startTasksPolling();
  }
  indicesInfoLoading.value = false;
}

async function triggerResourceMaintenance() {
  resourceMaintenanceLoading.value = true;
  const { data, error } = await GET('/resources/maintenance');
  if (!error) {
    addTask(data);
    message.info($t('admin.system.maintenance.resourceMaintenance.actionStarted'));
    startTasksPolling();
  }
  resourceMaintenanceLoading.value = false;
}

async function deleteTask(id: string) {
  tasksLoading.value = true;
  const { error } = await DELETE('/platform/tasks/{id}', { params: { path: { id } } });
  if (!error) {
    allTasks.value = allTasks.value.filter((task) => task.id !== id);
  }
  tasksLoading.value = false;
}

async function deleteSystemTasks() {
  tasksLoading.value = true;
  const { data, error } = await DELETE('/platform/tasks/system');
  if (!error) {
    message.success($t('admin.system.maintenance.tasks.actionDeleteAllSuccess'));
    allTasks.value = data;
  }
  tasksLoading.value = false;
}

async function deleteAllTasks() {
  tasksLoading.value = true;
  const { error } = await DELETE('/platform/tasks/all');
  if (!error) {
    message.success($t('admin.system.maintenance.tasks.actionDeleteAllSuccess'));
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
  const maxFieldMappings = pfData.value?.maxFieldMappings || 0;
  if (fields > maxFieldMappings * 0.9) {
    return 'over';
  } else if (fields > maxFieldMappings * 0.75) {
    return 'near';
  } else {
    return 'ok';
  }
}

onBeforeMount(() => {
  loadIndexInfo();
  updateAllTasksData();
});
</script>

<template>
  <icon-heading level="2" :icon="MaintenanceIcon">
    {{ $t('admin.system.maintenance.heading') }}
    <help-button-widget help-key="adminSystemMaintenanceView" />
  </icon-heading>

  <div class="content-block">
    <!-- SEARCH INDICES -->
    <h3>{{ $t('admin.system.maintenance.indices.heading') }}</h3>

    <n-flex style="margin: var(--layout-gap) 0">
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
        {{ $t('admin.system.maintenance.indices.actionCreate') }}
      </n-button>
    </n-flex>

    <n-table size="small" style="table-layout: fixed" :bordered="false" :bottom-bordered="false">
      <template v-for="(indexInfo, i) in indicesInfo" :key="`${i}_${indexInfo.textId}`">
        <thead>
          <tr>
            <th
              colspan="2"
              :style="{
                backgroundColor: theme.generateAccentColorVariants(
                  pfData?.texts.find((t) => t.id === indexInfo.textId)?.accentColor
                ).fade4,
              }"
            >
              {{ pfData?.texts.find((t) => t.id === indexInfo.textId)?.title || '???' }}
            </th>
          </tr>
        </thead>
        <template v-for="(value, key) in indexInfo" :key="key">
          <tr v-if="!['createdAt', 'textId', 'fields'].includes(key)">
            <th style="font-weight: var(--font-weight-normal)">
              {{ $t(`admin.system.maintenance.indices.${key}`) }}
            </th>
            <td>{{ value }}</td>
          </tr>
        </template>
        <tr>
          <th style="font-weight: var(--font-weight-normal)">
            {{ $t(`admin.system.maintenance.indices.fields`) }}
          </th>
          <td :class="`max-fields-warn-${getFieldMappingsStatus(indexInfo.fields)}`">
            {{ indexInfo.fields }} / {{ pfData?.maxFieldMappings || '???' }}
          </td>
        </tr>
        <tr>
          <th style="font-weight: var(--font-weight-normal)">
            {{ $t(`admin.system.maintenance.indices.createdAt`) }}
          </th>
          <td>
            <n-time
              v-if="indexInfo.createdAt"
              :time="utcToLocalTime(indexInfo.createdAt)"
              type="datetime"
            />
            <span v-else>???</span>
          </td>
        </tr>
      </template>
    </n-table>

    <!-- RESOURCE MAINTENANCE -->
    <h3>{{ $t('admin.system.maintenance.resourceMaintenance.heading') }}</h3>

    <n-flex style="margin: var(--layout-gap) 0">
      <n-button
        secondary
        :disabled="resourceMaintenanceLoading"
        :loading="resourceMaintenanceLoading"
        @click="triggerResourceMaintenance"
      >
        <template #icon>
          <n-icon :component="MaintenanceIcon" />
        </template>
        {{ $t('general.runAction') }}
      </n-button>
    </n-flex>

    <!-- SYSTEM BACKGROUND TASKS -->
    <h3>{{ $t('tasks.title') }}</h3>

    <n-flex style="margin: var(--layout-gap) 0">
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
        :disabled="tasksLoading"
        :loading="tasksLoading"
        @click="deleteSystemTasks"
      >
        <template #icon>
          <n-icon :component="DeleteIcon" />
        </template>
        {{ $t('admin.system.maintenance.tasks.actionDeleteSystem') }}
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
        {{ $t('admin.system.maintenance.tasks.actionDeleteAll') }}
      </n-button>
    </n-flex>

    <template v-if="allTasks.length">
      <n-table size="small" style="table-layout: fixed">
        <thead>
          <tr>
            <th>{{ $t('admin.system.maintenance.tasks.type') }}</th>
            <th>{{ $t('admin.system.maintenance.tasks.status') }}</th>
            <th>{{ $t('admin.system.maintenance.tasks.started') }}</th>
            <th>{{ $t('admin.system.maintenance.tasks.ended') }}</th>
            <th>{{ $t('admin.system.maintenance.tasks.duration') }}</th>
            <th>{{ $t('admin.system.maintenance.tasks.startedBy') }}</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
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
                  ? $t('admin.system.maintenance.tasks.seconds', {
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
      </n-table>
    </template>
    <div v-else>
      {{ $t('admin.system.maintenance.tasks.noTasks') }}
    </div>
  </div>
</template>

<style scoped>
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
  color: var(--col-warning);
  font-weight: var(--font-weight-bold);
}

.max-fields-warn-over {
  color: var(--col-error);
  font-weight: var(--font-weight-bold);
}
</style>
