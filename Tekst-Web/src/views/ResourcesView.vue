<script setup lang="ts">
import {
  NButton,
  NInput,
  NIcon,
  NFlex,
  NSpin,
  NPagination,
  NList,
  NCollapse,
  NCollapseItem,
  useDialog,
} from 'naive-ui';
import {
  POST,
  type AnyResourceRead,
  DELETE,
  type UserReadPublic,
  GET,
  withSelectedFile,
} from '@/api';
import { onMounted, ref } from 'vue';
import { computed } from 'vue';
import { $t } from '@/i18n';
import { useAuthStore, useStateStore } from '@/stores';
import ResourceListItem from '@/components/resource/ResourceListItem.vue';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import { dialogProps } from '@/common';
import { useMessages } from '@/composables/messages';
import { useRouter } from 'vue-router';
import { useResourcesStore } from '@/stores';
import TransferResourceModal from '@/components/modals/TransferResourceModal.vue';
import { saveDownload } from '@/api';
import { SearchIcon, UndoIcon, ResourceIcon, AddIcon } from '@/icons';
import LabelledSwitch from '@/components/LabelledSwitch.vue';
import { useTasks } from '@/composables/tasks';
import { pickTranslation } from '@/utils';
import { createReusableTemplate } from '@vueuse/core';

const state = useStateStore();
const auth = useAuthStore();
const resources = useResourcesStore();
const dialog = useDialog();
const { message } = useMessages();
const router = useRouter();
const { addTask, startTasksPolling } = useTasks();
const [DefineTemplate, ReuseTemplate] = createReusableTemplate();

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
  return resourcesData.filter((r) => {
    const resourceStringContent = filters.value.search
      ? [
          r.title.map((t) => t.translation).join(' '),
          r.description?.map((d) => d.translation).join(' ') || '',
          r.ownerId,
          r.comment?.map((c) => c.translation).join(' ') || '',
          r.citation,
          JSON.stringify(r.meta),
        ]
          .filter((prop) => prop)
          .join(' ')
      : '';
    return (
      (!filters.value.search ||
        resourceStringContent.toLowerCase().includes(filters.value.search.toLowerCase())) &&
      ((filters.value.proposed && r.proposed) || (filters.value.notProposed && !r.proposed)) &&
      ((filters.value.public && r.public) || (filters.value.notPublic && !r.public)) &&
      ((filters.value.ownedByMe && r.ownerId === auth.user?.id) ||
        (filters.value.ownedByOthers && r.ownerId !== auth.user?.id))
    );
  });
}

const filteredData = computed(() => filterData(resources.ofText));
const paginatedData = computed(() => {
  const start = (pagination.value.page - 1) * pagination.value.pageSize;
  const end = start + pagination.value.pageSize;
  return filteredData.value
    .slice(start, end)
    .sort((a, b) => (b.corrections || 0) - (a.corrections || 0));
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
      $t('resources.msgTransferred', {
        title: pickTranslation(resource.title, state.locale),
        username: user.username,
      })
    );
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
    autoFocus: false,
    closable: false,
    ...dialogProps,
    onPositiveClick: async () => {
      actionsLoading.value = true;
      const { data, error } = await POST('/resources/{id}/propose', {
        params: { path: { id: resource.id } },
      });
      if (!error) {
        resources.replace(data);
        message.success(
          $t('resources.msgProposed', { title: pickTranslation(resource.title, state.locale) })
        );
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
    autoFocus: false,
    closable: false,
    ...dialogProps,
    onPositiveClick: async () => {
      actionsLoading.value = true;
      const { data, error } = await POST('/resources/{id}/unpropose', {
        params: { path: { id: resource.id } },
      });
      if (!error) {
        resources.replace(data);
        message.success(
          $t('resources.msgUnproposed', { title: pickTranslation(resource.title, state.locale) })
        );
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
    autoFocus: false,
    closable: false,
    ...dialogProps,
    onPositiveClick: async () => {
      actionsLoading.value = true;
      const { data, error } = await POST('/resources/{id}/publish', {
        params: { path: { id: resource.id } },
      });
      if (!error) {
        resources.replace(data);
        message.success(
          $t('resources.msgPublished', { title: pickTranslation(resource.title, state.locale) })
        );
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
    autoFocus: false,
    closable: false,
    ...dialogProps,
    onPositiveClick: async () => {
      actionsLoading.value = true;
      const { data, error } = await POST('/resources/{id}/unpublish', {
        params: { path: { id: resource.id } },
      });
      if (!error) {
        resources.replace(data);
        message.success(
          $t('resources.msgUnpublished', { title: pickTranslation(resource.title, state.locale) })
        );
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
    content: $t('resources.infoCreateVersion', {
      title: pickTranslation(resource.title, state.locale),
    }),
    positiveText: $t('general.yesAction'),
    negativeText: $t('general.noAction'),
    autoFocus: false,
    closable: false,
    ...dialogProps,
    onPositiveClick: async () => {
      actionsLoading.value = true;
      const { data, error } = await POST('/resources/{id}/version', {
        params: { path: { id: resource.id } },
      });
      if (!error) {
        resources.add(data);
        message.success(
          $t('resources.msgCreatedVersion', {
            title: pickTranslation(resource.title, state.locale),
          })
        );
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
    autoFocus: false,
    closable: false,
    ...dialogProps,
    onPositiveClick: async () => {
      actionsLoading.value = true;
      const { error } = await DELETE('/resources/{id}', {
        params: { path: { id: resource.id } },
      });
      if (!error) {
        message.success(
          $t('resources.msgDeleted', { title: pickTranslation(resource.title, state.locale) })
        );
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
    const resSaveName = pickTranslation(resource.title, state.locale)
      .substring(0, 32)
      .trim()
      .replace(/\W+/g, '_');
    const filename = `${resSaveName}_${resource.id}_template.json`.toLowerCase();
    message.info($t('general.downloadSaved', { filename }));
    saveDownload(await response.blob(), filename);
  }
  actionsLoading.value = false;
}

async function handleImportClick(resource: AnyResourceRead) {
  withSelectedFile(async (file: File | null) => {
    if (!file) return;
    actionsLoading.value = true;
    const { data, error } = await POST('/resources/{id}/import', {
      params: { path: { id: resource.id } },
      body: { file },
      bodySerializer(body) {
        const fd = new FormData();
        for (const [k, v] of Object.entries(body)) {
          fd.append(k, v);
        }
        return fd;
      },
    });
    if (!error) {
      addTask(data);
      message.info($t('contents.msgImportInfo'), undefined, 5);
      startTasksPolling();
    }
    actionsLoading.value = false;
  });
}

async function handleExportClick() {}

function handleFilterCollapseItemClick(data: { name: string; expanded: boolean }) {
  if (data.name === 'filters' && !data.expanded) {
    filters.value = initialFilters();
  }
}

onMounted(() => {
  // inform user in case there are corrections for resources of another text
  if (
    !resources.ofText.some((r) => !!r.corrections) &&
    resources.all.filter((r) => r.textId !== state.text?.id).some((r) => !!r.corrections)
  ) {
    message.info($t('resources.msgCorrections'));
  }
});
</script>

<template>
  <icon-heading level="1" :icon="ResourceIcon">
    {{ $t('resources.heading') }}
    <help-button-widget help-key="resourcesView" />
  </icon-heading>

  <define-template>
    <!-- Pagination -->
    <n-flex justify="end" class="pagination-container">
      <n-pagination
        v-model:page-size="pagination.pageSize"
        v-model:page="pagination.page"
        :page-sizes="[10, 20, 50, 100]"
        :default-page-size="10"
        :item-count="filteredData.length"
        show-size-picker
      />
    </n-flex>
  </define-template>

  <template v-if="resources.ofText && !resources.error && !loading">
    <!-- Filters -->
    <n-collapse
      style="margin-bottom: var(--layout-gap)"
      @item-header-click="handleFilterCollapseItemClick"
    >
      <n-collapse-item :title="$t('general.filters')" name="filters">
        <n-flex vertical class="gray-box">
          <n-input
            v-model:value="filters.search"
            :placeholder="$t('search.searchAction')"
            style="margin-bottom: var(--content-gap)"
            round
          >
            <template #prefix>
              <n-icon :component="SearchIcon" />
            </template>
          </n-input>
          <labelled-switch v-model="filters.public" :label="$t('resources.public')" />
          <labelled-switch v-model="filters.notPublic" :label="$t('resources.notPublic')" />
          <labelled-switch v-model="filters.proposed" :label="$t('resources.proposed')" />
          <labelled-switch v-model="filters.notProposed" :label="$t('resources.notProposed')" />
          <labelled-switch v-model="filters.ownedByMe" :label="$t('resources.ownedByMe')" />
          <labelled-switch v-model="filters.ownedByOthers" :label="$t('resources.ownedByOthers')" />
          <n-button style="margin-top: var(--content-gap)" @click="filters = initialFilters()">
            {{ $t('general.resetAction') }}
            <template #icon>
              <n-icon :component="UndoIcon" />
            </template>
          </n-button>
        </n-flex>
      </n-collapse-item>
    </n-collapse>

    <div class="resource-list-header">
      <div class="text-small translucent ellipsis">
        {{
          $t('resources.msgFoundCount', {
            count: filteredData.length,
            total: resources.ofText.length,
          })
        }}
      </div>
      <!-- Create new resource button -->
      <n-button v-if="auth.user" type="primary" @click="router.push({ name: 'resourceCreate' })">
        <template #icon>
          <n-icon :component="AddIcon" />
        </template>
        {{ $t('general.new') }}
      </n-button>
    </div>

    <!-- Resources List -->
    <div class="content-block">
      <template v-if="paginatedData.length > 0">
        <!-- Pagination -->
        <reuse-template />
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
        <reuse-template />
      </template>
      <template v-else>
        {{ $t('search.nothingFound') }}
      </template>
    </div>
  </template>

  <n-spin
    v-else-if="loading"
    size="large"
    class="centered-spinner"
    :description="$t('general.loading')"
  />

  <div v-else>
    {{ $t('errors.error') }}
  </div>

  <transfer-resource-modal
    :show="showTransferModal"
    :resource="transferTargetResource"
    :loading="actionsLoading"
    @update:show="($event: boolean) => (showTransferModal = $event)"
    @submit="handleTransferResource"
  />
</template>

<style scoped>
.resource-list-header {
  display: flex;
  justify-content: space-between;
  flex-wrap: nowrap;
  align-items: flex-end;
  max-width: 100%;
}

.pagination-container:first-child {
  margin-bottom: var(--layout-gap);
}
.pagination-container:last-child {
  margin-top: var(--layout-gap);
}
</style>
