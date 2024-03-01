<script setup lang="ts">
import { $t } from '@/i18n';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';

import IconHeading from '@/components/generic/IconHeading.vue';
import { MaintenanceIcon, PlayIcon } from '@/icons';
import { NSpace, NButton, NIcon, useDialog } from 'naive-ui';
import { GET } from '@/api';
import { useMessages } from '@/composables/messages';
import { onBeforeUnmount } from 'vue';
import { useLocks } from '@/composables/locks';
import { watch } from 'vue';

const { message } = useMessages();
const dialog = useDialog();

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

async function handleActionSearchIndexCreate() {
  indexLocked.value = true;
  const { error } = await GET('/admin/index/create');
  if (!error) {
    message.info($t('admin.system.maintenance.actionCreateIndexStarted'));
  }
  startIndexLockPolling();
}

async function handleActionGetIndexInfo() {
  const { data, error } = await GET('/admin/index/info');
  if (!error) {
    dialog.info({
      title: $t('admin.system.maintenance.actionGetIndexInfoDiagTitle'),
      content: JSON.stringify(data, null, 2),
      positiveText: $t('general.okAction'),
    });
  }
}

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
    <h4>{{ $t('admin.system.maintenance.headingSearchIndexActions') }}</h4>
    <n-space vertical>
      <n-space align="center">
        <n-button
          type="primary"
          size="small"
          :title="$t('admin.system.maintenance.actionCreateIndex')"
          circle
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
      <n-space align="center">
        <n-button
          type="primary"
          size="small"
          :title="$t('admin.system.maintenance.actionGetIndexInfo')"
          circle
          :disabled="indexLocked"
          :loading="indexLocked"
          @click="handleActionGetIndexInfo"
        >
          <template #icon>
            <n-icon :component="PlayIcon" />
          </template>
        </n-button>
        <div>{{ $t('admin.system.maintenance.actionGetIndexInfo') }}</div>
      </n-space>
    </n-space>
  </div>
</template>
