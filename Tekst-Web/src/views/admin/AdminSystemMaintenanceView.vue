<script setup lang="ts">
import { $t } from '@/i18n';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';

import IconHeading from '@/components/generic/IconHeading.vue';
import { MaintenanceIcon, PlayIcon } from '@/icons';
import { NSpace, NButton, NIcon, NTable } from 'naive-ui';
import { GET, type IndexInfoResponse } from '@/api';
import { useMessages } from '@/composables/messages';
import { onBeforeMount, onBeforeUnmount, ref } from 'vue';
import { useLocks } from '@/composables/locks';
import { watch } from 'vue';

const { message } = useMessages();

const {
  locked: indexLocked,
  start: startIndexLockPolling,
  stop: stopIndexLockPolling,
} = useLocks('index-create-update', {
  immediate: true,
  stopWhenUnlocked: true,
});
watch(indexLocked, (after) => {
  !after && message.success($t('admin.system.maintenance.actionCreateIndexSuccess'));
});

const indexInfo = ref<IndexInfoResponse>();

async function handleActionSearchIndexCreate() {
  indexLocked.value = true;
  const { error } = await GET('/admin/index/create');
  if (!error) {
    message.info($t('admin.system.maintenance.actionCreateIndexStarted'));
  }
  startIndexLockPolling();
}

async function loadIndexInfo() {
  const { data, error } = await GET('/admin/index/info');
  if (!error) {
    indexInfo.value = data;
  }
}

onBeforeMount(() => loadIndexInfo());
onBeforeUnmount(() => stopIndexLockPolling());
</script>

<template>
  <icon-heading level="2" :icon="MaintenanceIcon">
    {{ $t('admin.system.maintenance.heading') }}
    <help-button-widget help-key="adminSystemMaintenanceView" />
  </icon-heading>

  <div class="content-block">
    <!-- SEARCH INDEX -->
    <h3>{{ $t('admin.system.maintenance.headingSearchIndex') }}</h3>
    <tempalte v-if="indexInfo">
      <h4>{{ $t('admin.system.maintenance.indexInfo.heading') }}</h4>
      <n-table :bordered="true" size="small">
        <tbody>
          <tr v-for="(value, key) in indexInfo" :key="key">
            <th>{{ $t(`admin.system.maintenance.indexInfo.${key}`) }}</th>
            <td>{{ value }}</td>
          </tr>
        </tbody>
      </n-table>
    </tempalte>
    <h4>{{ $t('admin.system.maintenance.headingSearchIndexActions') }}</h4>
    <n-space vertical>
      <n-space align="center">
        <n-button
          type="primary"
          size="small"
          :title="$t('admin.system.maintenance.actionCreateIndex')"
          :disabled="indexLocked"
          :loading="indexLocked"
          @click="handleActionSearchIndexCreate"
        >
          <template #icon>
            <n-icon :component="PlayIcon" />
          </template>
        </n-button>
        <div>{{ $t('admin.system.maintenance.actionCreateIndex') }}</div>
      </n-space>
    </n-space>
  </div>
</template>
