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
import { POST, type AnyResourceRead, DELETE } from '@/api';
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

const state = useStateStore();
const auth = useAuthStore();
const resources = useResourcesStore();
const dialog = useDialog();
const { message } = useMessages();
const router = useRouter();

const actionsLoading = ref(false);
const loading = computed(() => actionsLoading.value || resources.loading);

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

function handleEditClick(resource: AnyResourceRead) {
  router.push({ name: 'resourceEdit', params: { text: state.text?.slug, id: resource.id } });
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

function handleFilterCollapseItemClick(data: { name: string; expanded: boolean }) {
  if (data.name === 'filters' && !data.expanded) {
    filters.value = initialFilters();
  }
}
</script>

<template>
  <IconHeading level="1" :icon="LayersFilled">
    {{ $t('resources.heading') }} {{ `(${resources.data.length})` }}
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
    <n-space justify="end">
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
            @propose-click="handleProposeClick"
            @unpropose-click="handleUnproposeClick"
            @publish-click="handlePublishClick"
            @unpublish-click="handleUnpublishClick"
            @edit-click="handleEditClick"
            @delete-click="handleDeleteClick"
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
</template>
