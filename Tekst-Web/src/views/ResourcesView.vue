<script setup lang="ts">
import {
  DELETE,
  downloadData,
  GET,
  POST,
  withSelectedFile,
  type AnyResourceRead,
  type UserReadPublic,
} from '@/api';
import { dialogProps } from '@/common';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import ListingsFilters from '@/components/ListingsFilters.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import TransferResourceModal from '@/components/modals/TransferResourceModal.vue';
import ResourceListItem from '@/components/resource/ResourceListItem.vue';
import { useMessages } from '@/composables/messages';
import { useTasks } from '@/composables/tasks';
import { $t } from '@/i18n';
import { AddIcon, ResourceIcon } from '@/icons';
import { useAuthStore, useResourcesStore, useStateStore, useUserMessagesStore } from '@/stores';
import { pickTranslation } from '@/utils';
import { createReusableTemplate } from '@vueuse/core';
import { NButton, NFlex, NIcon, NList, NPagination, NSpin, useDialog } from 'naive-ui';
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';

const props = defineProps<{
  textSlug?: string;
}>();

const state = useStateStore();
const auth = useAuthStore();
const resources = useResourcesStore();
const userMessages = useUserMessagesStore();
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
  pageSize: 20,
});

const filtersRef = ref<InstanceType<typeof ListingsFilters> | null>(null);
const filtersSearch = ref<string>();
const filtersFlags = ref<string[]>();

function filterData(resourcesData: AnyResourceRead[]) {
  pagination.value.page = 1;
  return resourcesData.filter((r) => {
    const resourceStringContent = filtersSearch.value
      ? [
          r.title.map((t) => t.translation).join(' '),
          r.subtitle.map((s) => s.translation).join(' ') || '',
          r.owner?.name || '',
          r.owner?.username || '',
          r.owner?.affiliation || '',
          r.description.map((d) => d.translation).join(' ') || '',
          r.citation,
          JSON.stringify(r.meta),
        ]
          .filter(Boolean)
          .join(' ')
      : '';
    return (
      (!filtersSearch.value ||
        resourceStringContent.toLowerCase().includes(filtersSearch.value.toLowerCase())) &&
      ((filtersFlags.value?.includes('proposed') && r.proposed) ||
        (filtersFlags.value?.includes('notProposed') && !r.proposed)) &&
      ((filtersFlags.value?.includes('public') && r.public) ||
        (filtersFlags.value?.includes('notPublic') && !r.public)) &&
      ((filtersFlags.value?.includes('ownedByMe') && r.ownerId === auth.user?.id) ||
        (filtersFlags.value?.includes('notOwnedByMe') && r.ownerId !== auth.user?.id)) &&
      ((filtersFlags.value?.includes('hasCorrections') && r.corrections) ||
        (filtersFlags.value?.includes('hasNoCorrections') && !r.corrections))
    );
  });
}

const filteredData = computed(() => filterData(resources.ofText));
const paginatedData = computed(() => {
  const start = (pagination.value.page - 1) * pagination.value.pageSize;
  const end = start + pagination.value.pageSize;
  return filteredData.value
    .filter((r) => !!r) // just to prevent side effects of sort()
    .sort((a, b) => {
      // resource has correction notes
      let diff = (b.corrections || 0) - (a.corrections || 0);
      if (diff !== 0) return diff;
      // resource is not published
      diff = (!b.public ? 1 : 0) - (!a.public ? 1 : 0);
      if (diff !== 0) return diff;
      // resource is owned by me
      diff = (b.ownerId === auth.user?.id ? 1 : 0) - (a.ownerId === auth.user?.id ? 1 : 0);
      if (diff !== 0) return diff;
      // otherwise, sort by ID (age ascending, effectively)
      return b.id.localeCompare(a.id);
    })
    .slice(start, end);
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
  filtersRef.value?.reset();
  showTransferModal.value = false;
  transferTargetResource.value = undefined;
  actionsLoading.value = false;
}

function handleProposeClick(resource: AnyResourceRead) {
  dialog.warning({
    title: $t('common.warning'),
    content: $t('resources.warnPropose') + ' ' + $t('common.areYouSureHelpTextHint'),
    positiveText: $t('common.yes'),
    negativeText: $t('common.no'),
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
      filtersRef.value?.reset();
      actionsLoading.value = false;
    },
  });
}

function handleUnproposeClick(resource: AnyResourceRead) {
  dialog.warning({
    title: $t('common.warning'),
    content: $t('resources.warnUnpropose'),
    positiveText: $t('common.yes'),
    negativeText: $t('common.no'),
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
      filtersRef.value?.reset();
      actionsLoading.value = false;
    },
  });
}

function handlePublishClick(resource: AnyResourceRead) {
  dialog.warning({
    title: $t('common.warning'),
    content: $t('resources.warnPublish') + ' ' + $t('common.areYouSureHelpTextHint'),
    positiveText: $t('common.yes'),
    negativeText: $t('common.no'),
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
      filtersRef.value?.reset();
      actionsLoading.value = false;
    },
  });
}

function handleUnpublishClick(resource: AnyResourceRead) {
  dialog.warning({
    title: $t('common.warning'),
    content: $t('resources.warnUnpublish'),
    positiveText: $t('common.yes'),
    negativeText: $t('common.no'),
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
      filtersRef.value?.reset();
      actionsLoading.value = false;
    },
  });
}

function handleSettingsClick(resource: AnyResourceRead) {
  router.push({
    name: 'resourceSettings',
    params: { textSlug: props.textSlug, id: resource.id },
  });
}

function handleContentsClick(resource: AnyResourceRead) {
  router.push({
    name: 'resourceContents',
    params: { textSlug: props.textSlug, resId: resource.id },
  });
}

function handleCreateVersionClick(resource: AnyResourceRead) {
  dialog.warning({
    title: $t('common.information'),
    content: $t('resources.infoCreateVersion', {
      title: pickTranslation(resource.title, state.locale),
    }),
    positiveText: $t('common.yes'),
    negativeText: $t('common.no'),
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
    title: $t('common.warning'),
    content: $t('resources.warnDelete'),
    positiveText: $t('common.yes'),
    negativeText: $t('common.no'),
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
  const { data, error } = await GET('/resources/{id}/template', {
    params: { path: { id: resource.id } },
    parseAs: 'blob',
  });
  if (!error) {
    const resSaveName = pickTranslation(resource.title, state.locale)
      .substring(0, 32)
      .trim()
      .replace(/\W+/g, '_');
    const filename = `${resSaveName}_${resource.id}_template.json`.toLowerCase();
    message.info($t('common.downloadSaved', { filename }));
    downloadData(data, filename);
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

function handleReqVersionIntegrationClick(resourceVersion: AnyResourceRead) {
  const originalResource = resources.all.find((r) => r.id === resourceVersion.originalId);
  if (!originalResource) {
    console.error(`No original resource found for version ${resourceVersion}`);
    return;
  }
  if (!originalResource.ownerId) {
    console.error(`No owner ID found for original resource ${originalResource}`);
    return;
  }
  const versionTitle = pickTranslation(resourceVersion.title, state.locale);
  const originalTitle = pickTranslation(originalResource.title, state.locale);
  const prepMsg = `> ${versionTitle} → ${originalTitle}\n\n`;
  userMessages.openConversation(originalResource.ownerId, prepMsg);
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
        :simple="state.smallScreen"
        :page-sizes="[10, 20, 50, 100]"
        :item-count="filteredData.length"
        size="medium"
        show-size-picker
      />
    </n-flex>
  </define-template>

  <template v-if="resources.ofText && !resources.error && !loading">
    <!-- Filters -->
    <listings-filters
      ref="filtersRef"
      v-model:search="filtersSearch"
      v-model:flags="filtersFlags"
      :flags-labels="{
        public: $t('resources.public'),
        notPublic: $t('resources.notPublic'),
        proposed: $t('resources.proposed'),
        notProposed: $t('resources.notProposed'),
        ownedByMe: $t('resources.ownedByMe'),
        ownedByOthers: $t('resources.ownedByOthers'),
        hasCorrections: $t('resources.hasCorrections'),
        hasNoCorrections: $t('resources.hasNoCorrections'),
      }"
    />

    <!-- List Header -->
    <n-flex justify="space-between" align="center">
      <div class="text-small translucent ellipsis">
        {{
          $t('resources.msgFoundCount', {
            count: filteredData.length,
            total: resources.ofText.length,
          })
        }}
      </div>
      <!-- Create new resource button -->
      <n-button
        v-if="auth.user"
        type="primary"
        @click="router.push({ name: 'resourceCreate', params: { textSlug: props.textSlug } })"
      >
        <template #icon>
          <n-icon :component="AddIcon" />
        </template>
        {{ $t('resources.new') }}
      </n-button>
    </n-flex>

    <!-- Resources List -->
    <div class="content-block">
      <template v-if="paginatedData.length > 0">
        <!-- Pagination -->
        <reuse-template />
        <n-list style="background-color: transparent">
          <resource-list-item
            v-for="item in paginatedData"
            :key="item.id"
            :resource="item"
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
            @req-version-integration-click="handleReqVersionIntegrationClick"
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

  <n-spin v-else-if="loading" class="centered-spinner" :description="$t('common.loading')" />

  <div v-else>
    {{ $t('errors.error') }}
  </div>

  <transfer-resource-modal
    :show="showTransferModal"
    :resource="transferTargetResource"
    :loading="actionsLoading"
    @update:show="(v?: boolean) => (showTransferModal = !!v)"
    @submit="handleTransferResource"
  />
</template>

<style scoped>
.pagination-container:first-child {
  margin-bottom: var(--gap-lg);
}

.pagination-container:last-child {
  margin-top: var(--gap-lg);
}
</style>
