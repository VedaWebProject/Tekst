<script setup lang="ts">
import {
  NButton,
  NInput,
  NIcon,
  NCheckbox,
  NSpace,
  NSpin,
  NPagination,
  NList,
  NCollapse,
  NCollapseItem,
  useDialog,
} from 'naive-ui';
import { POST, type AnyResourceRead, DELETE, type UserReadPublic, getFullUrl, GET } from '@/api';
import { ref } from 'vue';
import { computed } from 'vue';
import { $t } from '@/i18n';
import { useAuthStore, useStateStore } from '@/stores';
import ResourceListItem from '@/components/ResourceListItem.vue';
import HelpButtonWidget from '@/components/widgets/HelpButtonWidget.vue';
import IconHeading from '@/components/typography/IconHeading.vue';
import { negativeButtonProps, positiveButtonProps } from '@/components/dialogButtonProps';
import { useMessages } from '@/messages';
import { useRouter } from 'vue-router';
import { useResourcesStore } from '@/stores';

import SearchRound from '@vicons/material/SearchRound';
import UndoRound from '@vicons/material/UndoRound';
import LayersFilled from '@vicons/material/LayersFilled';
import AddOutlined from '@vicons/material/AddOutlined';
import TransferResourceModal from '@/components/TransferResourceModal.vue';
import { saveDownload } from '@/api';

const state = useStateStore();
const auth = useAuthStore();
const resources = useResourcesStore();
const dialog = useDialog();
const { message } = useMessages();
const router = useRouter();

const actionsLoading = ref(false);
const loading = computed(() => actionsLoading.value || resources.loading);

const transferTargetResource = ref<AnyResourceRead>();
const showTransferModal = ref(false);

const pagination = ref({
  page: 1,
  pageSize: 10,
});

const initialFilters = () => ({
  search: '',
  public: true,
  notPublic: true,
  proposed: true,
  notProposed: true,
  ownedByMe: true,
  ownedByOthers: true,
});

const filters = ref(initialFilters());

function filterData(resourcesData: AnyResourceRead[]) {
  pagination.value.page = 1;
  return resourcesData.filter((l) => {
    const resourceStringContent = filters.value.search
      ? [l.title, l.description, l.ownerId, l.comment, l.citation, JSON.stringify(l.meta)]
          .filter((prop) => prop)
          .join(' ')
      : '';
    return (
      (!filters.value.search ||
        resourceStringContent.toLowerCase().includes(filters.value.search.toLowerCase())) &&
      ((filters.value.proposed && l.proposed) || (filters.value.notProposed && !l.proposed)) &&
      ((filters.value.public && l.public) || (filters.value.notPublic && !l.public)) &&
      ((filters.value.ownedByMe && l.ownerId === auth.user?.id) ||
        (filters.value.ownedByOthers && l.ownerId !== auth.user?.id))
    );
  });
}

const filteredData = computed(() => filterData(resources.data));
const paginatedData = computed(() => {
  const start = (pagination.value.page - 1) * pagination.value.pageSize;
  const end = start + pagination.value.pageSize;
  return filteredData.value.slice(start, end);
});

async function handleTransferClick(resource: AnyResourceRead) {
  transferTargetResource.value = resource;
  showTransferModal.value = true;
}

async function handleTransferResource(resource?: AnyResourceRead, user?: UserReadPublic) {
  if (!resource || !user) return;
  actionsLoading.value = true;
  const { data, error } = await POST('/resources/{id}/transfer', {
    params: { path: { id: resource.id } },
    body: user.id,
  });
  if (!error) {
    resources.replace(data);
    message.success(
      $t('resources.msgTransferred', { title: resource.title, username: user.username })
    );
  } else {
    message.error($t('errors.unexpected'), error);
  }
  filters.value = initialFilters();
  showTransferModal.value = false;
  transferTargetResource.value = undefined;
  actionsLoading.value = false;
}

function handleProposeClick(resource: AnyResourceRead) {
  dialog.warning({
    title: $t('general.warning'),
    content: $t('resources.warnPropose') + ' ' + $t('general.areYouSureHelpTextHint'),
    positiveText: $t('general.yesAction'),
    negativeText: $t('general.noAction'),
    positiveButtonProps,
    negativeButtonProps,
    autoFocus: false,
    closable: false,
    onPositiveClick: async () => {
      actionsLoading.value = true;
      const { data, error } = await POST('/resources/{id}/propose', {
        params: { path: { id: resource.id } },
      });
      if (!error) {
        resources.replace(data);
        message.success($t('resources.msgProposed', { title: resource.title }));
      } else {
        message.error($t('errors.unexpected'), error);
      }
      filters.value = initialFilters();
      actionsLoading.value = false;
    },
  });
}

function handleUnproposeClick(resource: AnyResourceRead) {
  dialog.warning({
    title: $t('general.warning'),
    content: $t('resources.warnUnpropose'),
    positiveText: $t('general.yesAction'),
    negativeText: $t('general.noAction'),
    positiveButtonProps,
    negativeButtonProps,
    autoFocus: false,
    closable: false,
    onPositiveClick: async () => {
      actionsLoading.value = true;
      const { data, error } = await POST('/resources/{id}/unpropose', {
        params: { path: { id: resource.id } },
      });
      if (!error) {
        resources.replace(data);
        message.success($t('resources.msgUnproposed', { title: resource.title }));
      } else {
        message.error($t('errors.unexpected'), error);
      }
      filters.value = initialFilters();
      actionsLoading.value = false;
    },
  });
}

function handlePublishClick(resource: AnyResourceRead) {
  dialog.warning({
    title: $t('general.warning'),
    content: $t('resources.warnPublish') + ' ' + $t('general.areYouSureHelpTextHint'),
    positiveText: $t('general.yesAction'),
    negativeText: $t('general.noAction'),
    positiveButtonProps,
    negativeButtonProps,
    autoFocus: false,
    closable: false,
    onPositiveClick: async () => {
      actionsLoading.value = true;
      const { data, error } = await POST('/resources/{id}/publish', {
        params: { path: { id: resource.id } },
      });
      if (!error) {
        resources.replace(data);
        message.success($t('resources.msgPublished', { title: resource.title }));
      } else {
        message.error($t('errors.unexpected'), error);
      }
      filters.value = initialFilters();
      actionsLoading.value = false;
    },
  });
}

function handleUnpublishClick(resource: AnyResourceRead) {
  dialog.warning({
    title: $t('general.warning'),
    content: $t('resources.warnUnpublish'),
    positiveText: $t('general.yesAction'),
    negativeText: $t('general.noAction'),
    positiveButtonProps,
    negativeButtonProps,
    autoFocus: false,
    closable: false,
    onPositiveClick: async () => {
      actionsLoading.value = true;
      const { data, error } = await POST('/resources/{id}/unpublish', {
        params: { path: { id: resource.id } },
      });
      if (!error) {
        resources.replace(data);
        message.success($t('resources.msgUnpublished', { title: resource.title }));
      } else {
        message.error($t('errors.unexpected'), error);
      }
      filters.value = initialFilters();
      actionsLoading.value = false;
    },
  });
}

function handleSettingsClick(resource: AnyResourceRead) {
  router.push({ name: 'resourceSettings', params: { text: state.text?.slug, id: resource.id } });
}

function handleContentsClick(resource: AnyResourceRead) {
  router.push({
    name: 'resourceContents',
    params: { text: state.text?.slug, id: resource.id, pos: 0 },
  });
}

function handleCreateVersionClick(resource: AnyResourceRead) {
  dialog.warning({
    title: $t('general.info'),
    content: $t('resources.infoCreateVersion', { title: resource.title }),
    positiveText: $t('general.yesAction'),
    negativeText: $t('general.noAction'),
    positiveButtonProps,
    negativeButtonProps,
    autoFocus: false,
    closable: false,
    onPositiveClick: async () => {
      actionsLoading.value = true;
      const { data, error } = await POST('/resources/{id}/version', {
        params: { path: { id: resource.id } },
      });
      if (!error) {
        resources.add(data);
        message.success($t('resources.msgCreatedVersion', { title: resource.title }));
      } else {
        message.error($t('errors.unexpected'), error);
      }
      actionsLoading.value = false;
    },
  });
}

function handleDeleteClick(resource: AnyResourceRead) {
  dialog.warning({
    title: $t('general.warning'),
    content: $t('resources.warnDelete'),
    positiveText: $t('general.yesAction'),
    negativeText: $t('general.noAction'),
    positiveButtonProps,
    negativeButtonProps,
    autoFocus: false,
    closable: false,
    onPositiveClick: async () => {
      actionsLoading.value = true;
      const { error } = await DELETE('/resources/{id}', {
        params: { path: { id: resource.id } },
      });
      if (!error) {
        message.success($t('resources.msgDeleted', { title: resource.title }));
      } else {
        message.error($t('errors.unexpected'), error);
      }
      await resources.load();
      actionsLoading.value = false;
    },
  });
}

async function handleDownloadTemplateClick(resource: AnyResourceRead) {
  actionsLoading.value = true;
  const { response, error } = await GET('/resources/{id}/template', {
    params: { path: { id: resource.id } },
    parseAs: 'blob',
  });
  if (!error) {
    const resSaveName = resource.title.substring(0, 32).trim().replace(/\W+/g, '_');
    const filename = `${resSaveName}_${resource.id}_template.json`.toLowerCase();
    message.info($t('general.downloadSaved', { filename }));
    saveDownload(await response.blob(), filename);
  } else {
    message.error($t('errors.unexpected'), error);
  }
  actionsLoading.value = false;
}

async function handleImportClick(resource: AnyResourceRead) {
  // unfortunately, this file upload doesn't work with our generated API client :(
  const path = `/resources/${resource.id || ''}/import`;
  const endpointUrl = getFullUrl(path);
  const input = document.createElement('input');
  input.type = 'file';
  input.accept = 'application/json,.json';

  input.onchange = async () => {
    if (!input.files) return;
    actionsLoading.value = true;
    const formData = new FormData();
    formData.append('file', input.files[0]);
    try {
      const response = await fetch(endpointUrl, {
        method: 'POST',
        headers: {
          Accept: 'application/json',
        },
        body: formData,
      });
      if (response.ok) {
        const resp = await response.json();
        message.success(
          $t('contents.msgImportSuccess', {
            updated: resp.updated,
            created: resp.created,
            errors: resp.errors,
          }),
          undefined,
          20
        );
      } else {
        message.error($t('errors.unexpected'), await response.json(), 20);
      }
    } catch {
      // failed request handled already, nothing to do
    } finally {
      input.remove();
      actionsLoading.value = false;
    }
  };

  input.onclose = () => {
    input.remove();
  };

  input.click();
}

async function handleExportClick() {}

function handleFilterCollapseItemClick(data: { name: string; expanded: boolean }) {
  if (data.name === 'filters' && !data.expanded) {
    filters.value = initialFilters();
  }
}
</script>

<template>
  <IconHeading level="1" :icon="LayersFilled">
    {{ $t('resources.heading') }}
    <HelpButtonWidget help-key="resourcesView" />
  </IconHeading>

  <template v-if="resources.data && !resources.error && !loading">
    <!-- Filters -->
    <n-collapse @item-header-click="handleFilterCollapseItemClick">
      <n-collapse-item :title="$t('general.filters')" name="filters">
        <n-input
          v-model:value="filters.search"
          :placeholder="$t('search.searchAction')"
          style="margin-bottom: 1rem"
          round
        >
          <template #prefix>
            <n-icon :component="SearchRound" />
          </template>
        </n-input>
        <n-space vertical justify="space-between" style="padding-left: 12px">
          <n-checkbox v-model:checked="filters.public" :label="$t('resources.public')" />
          <n-checkbox v-model:checked="filters.notPublic" :label="$t('resources.notPublic')" />
          <n-checkbox v-model:checked="filters.proposed" :label="$t('resources.proposed')" />
          <n-checkbox v-model:checked="filters.notProposed" :label="$t('resources.notProposed')" />
          <n-checkbox v-model:checked="filters.ownedByMe" :label="$t('resources.ownedByMe')" />
          <n-checkbox
            v-model:checked="filters.ownedByOthers"
            :label="$t('resources.ownedByOthers')"
          />
          <n-button
            secondary
            round
            style="margin-top: var(--content-gap)"
            @click="filters = initialFilters()"
          >
            {{ $t('general.resetAction') }}
            <template #icon>
              <n-icon :component="UndoRound" />
            </template>
          </n-button>
        </n-space>
      </n-collapse-item>
    </n-collapse>

    <!-- Create new resource button -->
    <n-space justify="space-between" align="center" style="margin-top: 0.5rem">
      <div style="margin-top: 0.5rem">
        {{
          $t('resources.msgFoundCount', {
            count: filteredData.length,
            total: resources.data.length,
          })
        }}
      </div>
      <n-button v-if="auth.user" type="primary" @click="router.push({ name: 'resourceCreate' })">
        <template #icon>
          <n-icon :component="AddOutlined" />
        </template>
        {{ $t('general.new') }}
      </n-button>
    </n-space>

    <!-- Resources List -->
    <div class="content-block">
      <template v-if="paginatedData.length > 0">
        <n-list style="background-color: transparent">
          <resource-list-item
            v-for="item in paginatedData"
            :key="item.id"
            :target-resource="item"
            :current-user="auth.user"
            @transfer-click="handleTransferClick"
            @propose-click="handleProposeClick"
            @unpropose-click="handleUnproposeClick"
            @publish-click="handlePublishClick"
            @unpublish-click="handleUnpublishClick"
            @settings-click="handleSettingsClick"
            @contents-click="handleContentsClick"
            @create-version-click="handleCreateVersionClick"
            @delete-click="handleDeleteClick"
            @download-template-click="handleDownloadTemplateClick"
            @import-click="handleImportClick"
            @export-click="handleExportClick"
          />
        </n-list>
        <!-- Pagination -->
        <div style="display: flex; justify-content: flex-end; padding-top: 12px">
          <n-pagination
            v-model:page-size="pagination.pageSize"
            v-model:page="pagination.page"
            :page-sizes="[10, 20, 50, 100]"
            :default-page-size="10"
            :item-count="filteredData.length"
            show-size-picker
          />
        </div>
      </template>
      <template v-else>
        {{ $t('search.nothingFound') }}
      </template>
    </div>
  </template>

  <n-spin
    v-else-if="loading"
    size="large"
    style="margin: 3rem 0 2rem 0; width: 100%"
    :description="$t('general.loading')"
  />

  <div v-else>
    {{ $t('errors.error') }}
  </div>

  <TransferResourceModal
    :show="showTransferModal"
    :resource="transferTargetResource"
    :loading="actionsLoading"
    @update:show="($event) => (showTransferModal = $event)"
    @submit="handleTransferResource"
  />
</template>
