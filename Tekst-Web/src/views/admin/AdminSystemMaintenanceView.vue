<script setup lang="ts">
import { $t } from '@/i18n';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';

import IconHeading from '@/components/generic/IconHeading.vue';
import { LockIcon, LockOpenIcon, MaintenanceIcon, UpdateIcon } from '@/icons';
import { NTime, NSpace, NButton, NIcon, NTable } from 'naive-ui';
import { DELETE, GET, type IndexInfoResponse } from '@/api';
import { useMessages } from '@/composables/messages';
import { onBeforeMount, onBeforeUnmount, ref } from 'vue';
import { useLocks } from '@/composables/locks';
import { watch } from 'vue';

const { message } = useMessages();

const {
  locks,
  start: startLockPolling,
  stop: stopLockPolling,
} = useLocks({
  immediate: true,
});
watch(
  () => locks.value?.['index_create_update'],
  (after, before) => {
    if (before !== undefined && after === false) {
      message.success($t('admin.system.maintenance.index.actionCreateSuccess'));
      loadIndexInfo();
    }
  }
);

const indexInfo = ref<IndexInfoResponse>();
const locksReleaseLoading = ref(false);

async function handleActionCreateIndex() {
  locks.value['index_create_update'] = true;
  const { error } = await GET('/search/index/create');
  if (!error) {
    message.info($t('admin.system.maintenance.index.actionCreateStarted'));
  }
}

async function handleActionReleaseLocks() {
  locksReleaseLoading.value = true;
  const { error } = await DELETE('/platform/locks');
  if (!error) {
    message.success($t('admin.system.maintenance.locks.actionReleaseSuccess'));
  }
  locksReleaseLoading.value = false;
}

async function loadIndexInfo() {
  const { data, error } = await GET('/search/index/info');
  if (!error) {
    indexInfo.value = data;
  }
}

onBeforeMount(() => {
  loadIndexInfo();
  startLockPolling();
});
onBeforeUnmount(() => stopLockPolling());
</script>

<template>
  <icon-heading level="2" :icon="MaintenanceIcon">
    {{ $t('admin.system.maintenance.heading') }}
    <help-button-widget help-key="adminSystemMaintenanceView" />
  </icon-heading>

  <div class="content-block">
    <!-- SEARCH INDEX -->
    <h3>{{ $t('admin.system.maintenance.index.heading') }}</h3>
    <template v-if="indexInfo">
      <n-table :bordered="false" size="small" style="table-layout: fixed">
        <tbody>
          <template v-for="(value, key) in indexInfo" :key="key">
            <tr v-if="!['lastIndexed'].includes(key)">
              <td>{{ $t(`admin.system.maintenance.index.${key}`) }}</td>
              <td>{{ value }}</td>
            </tr>
          </template>
          <tr>
            <td>{{ $t(`admin.system.maintenance.index.lastIndexed`) }}</td>
            <td>
              <n-time :time="new Date(indexInfo.lastIndexed)" type="datetime" />
            </td>
          </tr>
        </tbody>
      </n-table>
    </template>
    <n-space vertical style="margin-top: var(--layout-gap)">
      <n-space align="center">
        <n-button
          type="primary"
          size="small"
          :title="$t('admin.system.maintenance.index.actionCreate')"
          :disabled="locks['index_create_update'] === true"
          :loading="locks['index_create_update'] === true"
          @click="handleActionCreateIndex"
        >
          <template #icon>
            <n-icon :component="UpdateIcon" />
          </template>
        </n-button>
        <div>{{ $t('admin.system.maintenance.index.actionCreate') }}</div>
      </n-space>
    </n-space>

    <!-- SYSTEM LOCKS -->
    <h3>{{ $t('admin.system.maintenance.locks.heading') }}</h3>
    <template v-if="locks">
      <n-table :bordered="false" size="small" style="table-layout: fixed">
        <tbody>
          <tr v-for="(value, key) in locks" :key="key">
            <td>{{ $t(`admin.system.maintenance.locks.${key}`) }}</td>
            <td :style="{ color: value ? 'var(--col-error)' : 'var(--col-success)' }">
              <n-space align="center">
                <n-icon :component="value ? LockIcon : LockOpenIcon" />
                <div>
                  {{
                    value
                      ? $t('admin.system.maintenance.locks.locked')
                      : $t('admin.system.maintenance.locks.unlocked')
                  }}
                </div>
              </n-space>
            </td>
          </tr>
        </tbody>
      </n-table>
    </template>
    <n-space vertical style="margin-top: var(--layout-gap)">
      <n-space align="center">
        <n-button
          type="primary"
          size="small"
          :disabled="locksReleaseLoading"
          :loading="locksReleaseLoading"
          :title="$t('admin.system.maintenance.locks.actionRelease')"
          @click="handleActionReleaseLocks"
        >
          <template #icon>
            <n-icon :component="LockOpenIcon" />
          </template>
        </n-button>
        <div>{{ $t('admin.system.maintenance.locks.actionRelease') }}</div>
      </n-space>
    </n-space>
  </div>
</template>
