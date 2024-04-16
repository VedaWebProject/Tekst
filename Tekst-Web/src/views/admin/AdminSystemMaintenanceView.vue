<script setup lang="ts">
import { $t } from '@/i18n';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';

import IconHeading from '@/components/generic/IconHeading.vue';
import { ClearIcon, MaintenanceIcon, UpdateIcon } from '@/icons';
import { NTime, NFlex, NButton, NIcon, NTable } from 'naive-ui';
import { DELETE, GET, type IndexInfoResponse, type TaskRead } from '@/api';
import { useMessages } from '@/composables/messages';
import { onBeforeMount, ref } from 'vue';
import { useTasks } from '@/composables/tasks';
import { toLocalTime } from '@/utils';

const { message } = useMessages();
const { start: startTasksPolling } = useTasks();

const allTasks = ref<TaskRead[]>([]);
const indexInfo = ref<IndexInfoResponse>();
const tasksDeleteLoading = ref(false);
const tasksUpdateLoading = ref(false);

const statusColors: Record<string, string> = {
  waiting: 'inherit',
  running: 'var(--col-info)',
  done: 'var(--col-success)',
  failed: 'var(--col-error)',
};

async function createIndex() {
  const { error } = await GET('/search/index/create');
  if (!error) {
    message.info($t('admin.system.maintenance.index.actionCreateStarted'));
    startTasksPolling();
  }
}

async function deleteAllTasks() {
  tasksDeleteLoading.value = true;
  const { error } = await DELETE('/platform/tasks');
  if (!error) {
    message.success($t('admin.system.maintenance.tasks.actionDeleteSuccess'));
    allTasks.value = [];
  }
  tasksDeleteLoading.value = false;
}

async function updateAllTasksData() {
  tasksUpdateLoading.value = true;
  const { data, error } = await GET('/platform/tasks/all');
  if (!error) {
    allTasks.value = data.sort(
      (a, b) =>
        (b.startTime ? Date.parse(b.startTime) : 0) - (a.startTime ? Date.parse(a.startTime) : 0)
    );
  }
  tasksUpdateLoading.value = false;
}

async function loadIndexInfo() {
  const { data, error } = await GET('/search/index/info');
  if (!error) {
    indexInfo.value = data;
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
    <!-- SEARCH INDEX -->
    <h3>{{ $t('admin.system.maintenance.index.heading') }}</h3>

    <n-flex vertical style="margin: var(--layout-gap) 0">
      <n-flex align="center">
        <n-button
          secondary
          type="primary"
          size="small"
          :title="$t('admin.system.maintenance.index.actionCreate')"
          @click="createIndex"
        >
          <template #icon>
            <n-icon :component="UpdateIcon" />
          </template>
        </n-button>
        <div>{{ $t('admin.system.maintenance.index.actionCreate') }}</div>
      </n-flex>
    </n-flex>

    <template v-if="indexInfo">
      <n-table :bordered="false" size="small" style="table-layout: fixed">
        <template v-for="(value, key) in indexInfo" :key="key">
          <tr v-if="!['lastIndexed'].includes(key)">
            <th>{{ $t(`admin.system.maintenance.index.${key}`) }}</th>
            <td>{{ value }}</td>
          </tr>
        </template>
        <tr>
          <th>{{ $t(`admin.system.maintenance.index.lastIndexed`) }}</th>
          <td>
            <n-time :time="toLocalTime(indexInfo.lastIndexed)" type="datetime" />
          </td>
        </tr>
      </n-table>
    </template>

    <!-- SYSTEM BACKGROUND TASKS -->
    <h3>{{ $t('tasks.title') }}</h3>

    <n-flex vertical style="margin: var(--layout-gap) 0">
      <n-flex align="center">
        <n-button
          secondary
          type="primary"
          size="small"
          :title="$t('admin.system.maintenance.tasks.actionUpdate')"
          :disabled="tasksUpdateLoading"
          :loading="tasksUpdateLoading"
          @click="updateAllTasksData"
        >
          <template #icon>
            <n-icon :component="UpdateIcon" />
          </template>
        </n-button>
        <div>{{ $t('admin.system.maintenance.tasks.actionUpdate') }}</div>
      </n-flex>
      <n-flex align="center">
        <n-button
          secondary
          type="primary"
          size="small"
          :title="$t('admin.system.maintenance.tasks.actionDelete')"
          :disabled="tasksDeleteLoading"
          :loading="tasksDeleteLoading"
          @click="deleteAllTasks"
        >
          <template #icon>
            <n-icon :component="ClearIcon" />
          </template>
        </n-button>
        <div>{{ $t('admin.system.maintenance.tasks.actionDelete') }}</div>
      </n-flex>
    </n-flex>

    <template v-if="allTasks.length">
      <n-table :bordered="false" size="small" style="table-layout: fixed">
        <thead>
          <tr>
            <th>{{ $t('admin.system.maintenance.tasks.type') }}</th>
            <th>{{ $t('admin.system.maintenance.tasks.status') }}</th>
            <th>{{ $t('admin.system.maintenance.tasks.started') }}</th>
            <th>{{ $t('admin.system.maintenance.tasks.ended') }}</th>
            <th>{{ $t('admin.system.maintenance.tasks.duration') }}</th>
            <th>{{ $t('admin.system.maintenance.tasks.startedBy') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="task in allTasks" :key="task.id">
            <td>{{ $t(`tasks.types.${task.type}`) }}</td>
            <td :style="{ color: statusColors[task.status || 'running'] }">
              {{ $t(`tasks.statuses.${task.status}`) }}
            </td>
            <td>
              <n-time v-if="task.startTime" :time="toLocalTime(task.startTime)" type="datetime" />
              <span v-else>–</span>
            </td>
            <td>
              <n-time v-if="task.endTime" :time="toLocalTime(task.endTime)" type="datetime" />
              <span v-else>–</span>
            </td>
            <td>
              {{
                task.durationSeconds
                  ? $t('admin.system.maintenance.tasks.seconds', {
                      seconds: task.durationSeconds.toFixed(2),
                    })
                  : '–'
              }}
            </td>
            <td>
              {{ task.userId || $t('general.system') }}
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
.content-block :deep(.n-table),
.content-block :deep(.n-table td) {
  background-color: transparent;
}
</style>
