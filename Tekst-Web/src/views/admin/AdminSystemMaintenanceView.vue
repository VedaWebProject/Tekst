<script setup lang="ts">
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import { $t } from '@/i18n';

import { DELETE, GET, type IndexInfoResponse, type TaskRead } from '@/api';
import FormSection from '@/components/FormSection.vue';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import LabeledSwitch from '@/components/LabeledSwitch.vue';
import { useMessages } from '@/composables/messages';
import { useTasks } from '@/composables/tasks';
import { DeleteIcon, MaintenanceIcon, RefreshIcon, UpdateIcon } from '@/icons';
import { useStateStore, useThemeStore } from '@/stores';
import { utcToLocalTime } from '@/utils';
import {
  NButton,
  NDivider,
  NFlex,
  NIcon,
  NTable,
  NTabPane,
  NTabs,
  NTime,
  type TabsInst,
} from 'naive-ui';
import { onBeforeMount, ref, watch } from 'vue';
import { RouterLink } from 'vue-router';

const SANE_IDX_FIELDS_LIMIT = 1000;

const state = useStateStore();
const theme = useThemeStore();
const { message } = useMessages();
const { addTask, startTasksPolling } = useTasks();

const tabsRef = ref<TabsInst>();
const allTasks = ref<TaskRead[]>([]);
const indicesInfo = ref<IndexInfoResponse>();
const indicesInfoLoading = ref(false);
const indicesForce = ref(false);
const precomputedLoading = ref(false);
const precomputedForce = ref(false);
const cleanupLoading = ref(false);
const tasksLoading = ref(false);

const statusColors: Record<string, string> = {
  waiting: 'inherit',
  running: 'var(--info-color)',
  done: 'var(--success-color)',
  failed: 'var(--error-color)',
};

async function createIndex() {
  indicesInfoLoading.value = true;
  const { data, error } = await GET('/search/index/create', {
    params: { query: { force: indicesForce.value } },
  });
  if (!error) {
    addTask(data);
    message.info($t('admin.maintenance.indices.actionCreateStarted'));
    startTasksPolling();
    indicesForce.value = false;
  }
  indicesInfoLoading.value = false;
}

async function triggerPrecomputation() {
  precomputedLoading.value = true;
  const { data, error } = await GET('/resources/precompute', {
    params: { query: { force: precomputedForce.value } },
  });
  if (!error) {
    addTask(data);
    message.info($t('admin.maintenance.precomputed.actionStarted'));
    startTasksPolling();
    precomputedForce.value = false;
  }
  precomputedLoading.value = false;
}

async function triggerInternalCleanup() {
  cleanupLoading.value = true;
  const { data, error } = await GET('/platform/cleanup');
  if (!error) {
    addTask(data);
    message.info($t('admin.maintenance.cleanup.actionStarted'));
    startTasksPolling();
  }
  cleanupLoading.value = false;
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
  if (fields > SANE_IDX_FIELDS_LIMIT * 0.9) {
    return 'over';
  } else if (fields > SANE_IDX_FIELDS_LIMIT * 0.75) {
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
      <n-tab-pane :tab="$t('admin.maintenance.indices.heading')" name="indices">
        <form-section :title="$t('admin.maintenance.indices.heading')" :show-box="false">
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
                {{ $t('common.refresh') }}
              </n-button>
              <n-divider vertical style="height: 100%" />
              <n-button secondary :disabled="indicesInfoLoading" @click="createIndex">
                <template #icon>
                  <n-icon :component="UpdateIcon" />
                </template>
                {{ $t('admin.maintenance.indices.actionCreate') }}
              </n-button>
              <labeled-switch
                v-model="indicesForce"
                :label="$t('admin.maintenance.force')"
                :title="$t('admin.maintenance.forceTip')"
              />
            </template>
          </button-shelf>

          <n-table size="small" style="table-layout: fixed" :bordered="false" class="mb-lg">
            <template v-for="(indexInfo, i) in indicesInfo" :key="`${i}_${indexInfo.textId}`">
              <tr>
                <th
                  colspan="2"
                  :style="{
                    backgroundColor: theme.getAccentColors(indexInfo.textId).fade5,
                  }"
                >
                  {{ state.textById(indexInfo.textId)?.title || '???' }}
                </th>
              </tr>
              <template v-for="(value, key) in indexInfo" :key="key">
                <tr v-if="!['textId', 'fields', 'upToDate'].includes(key)">
                  <th>
                    {{ $t(`admin.maintenance.indices.${key}`) }}
                  </th>
                  <td>{{ value }}</td>
                </tr>
              </template>
              <tr>
                <th>
                  {{ $t(`admin.maintenance.indices.fields`) }}
                </th>
                <td>
                  <n-flex align="center">
                    <span :class="`max-fields-warn-${getFieldMappingsStatus(indexInfo.fields)}`">
                      {{ indexInfo.fields }} / {{ SANE_IDX_FIELDS_LIMIT }}
                    </span>
                    <help-button-widget help-key="maxIndexFields" />
                  </n-flex>
                </td>
              </tr>
              <tr>
                <th>
                  {{ $t('common.status') }}
                </th>
                <td>
                  <span
                    :class="{ 'index-ood': !indexInfo.upToDate, 'index-utd': indexInfo.upToDate }"
                  >
                    {{
                      indexInfo.upToDate
                        ? $t('admin.maintenance.indices.utd')
                        : $t('admin.maintenance.indices.ood')
                    }}
                  </span>
                </td>
              </tr>
            </template>
          </n-table>
        </form-section>
      </n-tab-pane>

      <!-- PRECOMPUTED DATA ON RESOURCES -->
      <n-tab-pane :tab="$t('admin.maintenance.precomputed.heading')" name="precomputed">
        <form-section :title="$t('admin.maintenance.precomputed.heading')" :show-box="false">
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
                {{ $t('common.run') }}
              </n-button>
              <labeled-switch
                v-model="precomputedForce"
                :label="$t('admin.maintenance.force')"
                :title="$t('admin.maintenance.forceTip')"
              />
            </template>
          </button-shelf>
          <p>{{ $t('admin.maintenance.precomputed.description') }}</p>
        </form-section>
      </n-tab-pane>

      <!-- INTERNAL CLEANUP -->
      <n-tab-pane :tab="$t('admin.maintenance.cleanup.heading')" name="cleanup">
        <form-section :title="$t('admin.maintenance.cleanup.heading')" :show-box="false">
          <n-button
            secondary
            :disabled="cleanupLoading"
            :loading="cleanupLoading"
            @click="triggerInternalCleanup"
          >
            <template #icon>
              <n-icon :component="UpdateIcon" />
            </template>
            {{ $t('common.run') }}
          </n-button>
          <p>{{ $t('admin.maintenance.cleanup.description') }}</p>
        </form-section>
      </n-tab-pane>

      <!-- SYSTEM BACKGROUND TASKS -->
      <n-tab-pane :tab="$t('tasks.title')" name="tasks">
        <form-section :title="$t('tasks.title')" :show-box="false">
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
                {{ $t('common.refresh') }}
              </n-button>
            </template>
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
          </button-shelf>

          <n-table size="small" style="table-layout: fixed">
            <thead>
              <tr>
                <th>{{ $t('common.type') }}</th>
                <th>{{ $t('common.status') }}</th>
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
                  <n-time
                    v-if="task.endTime"
                    :time="utcToLocalTime(task.endTime)"
                    type="datetime"
                  />
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
                    {{ $t('common.system') }}
                  </span>
                </td>
                <td class="nowrap">
                  <n-button
                    secondary
                    size="small"
                    :title="$t('common.delete')"
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
        </form-section>
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

.max-fields-warn-ok {
  color: var(--success-color);
}

.max-fields-warn-ok::after {
  content: ' ✔';
}

.max-fields-warn-near {
  color: var(--warning-color);
  font-weight: bold;
}

.max-fields-warn-near::after {
  content: ' ⚠';
}

.max-fields-warn-over {
  color: var(--error-color);
  font-weight: bold;
}

.max-fields-warn-over::after {
  content: ' ⚠ ⚠ ⚠';
}

.index-ood {
  color: var(--error-color);
  font-weight: bold;
}

.index-ood::after {
  content: ' ⚠';
}

.index-utd {
  color: var(--success-color);
}

.index-utd::after {
  content: ' ✔';
}
</style>
