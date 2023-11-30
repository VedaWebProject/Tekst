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
import { POST, type AnyLayerRead, DELETE } from '@/api';
import { ref } from 'vue';
import { computed } from 'vue';
import { $t } from '@/i18n';
import { useAuthStore, useBrowseStore, useStateStore } from '@/stores';
import LayerListItem from '@/components/LayerListItem.vue';
import { useLayers } from '@/fetchers';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import IconHeading from '@/components/typography/IconHeading.vue';
import { negativeButtonProps, positiveButtonProps } from '@/components/dialogButtonProps';
import { useMessages } from '@/messages';

import SearchRound from '@vicons/material/SearchRound';
import UndoRound from '@vicons/material/UndoRound';
import LayersFilled from '@vicons/material/LayersFilled';
import { useRouter } from 'vue-router';

const state = useStateStore();
const browse = useBrowseStore();
const auth = useAuthStore();
const dialog = useDialog();
const { message } = useMessages();
const router = useRouter();

const textId = computed(() => state.text?.id || '');
const { layers, loading, error, load } = useLayers(textId);

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

function filterData(layers: AnyLayerRead[]) {
  pagination.value.page = 1;
  return layers.filter((l) => {
    const layerStringContent = filters.value.search
      ? [l.title, l.description, l.ownerId, l.comment, l.citation, JSON.stringify(l.meta)]
          .filter((prop) => prop)
          .join(' ')
      : '';
    return (
      (!filters.value.search ||
        layerStringContent.toLowerCase().includes(filters.value.search.toLowerCase())) &&
      ((filters.value.proposed && l.proposed) || (filters.value.notProposed && !l.proposed)) &&
      ((filters.value.public && l.public) || (filters.value.notPublic && !l.public)) &&
      ((filters.value.ownedByMe && l.ownerId === auth.user?.id) ||
        (filters.value.ownedByOthers && l.ownerId !== auth.user?.id))
    );
  });
}

const filteredData = computed(() => filterData(layers.value || []));
const paginatedData = computed(() => {
  const start = (pagination.value.page - 1) * pagination.value.pageSize;
  const end = start + pagination.value.pageSize;
  return filteredData.value.slice(start, end);
});

function handleProposeClick(layer: AnyLayerRead) {
  dialog.warning({
    title: $t('general.warning'),
    content: $t('dataLayers.warnPropose') + ' ' + $t('general.areYouSureHelpTextHint'),
    positiveText: $t('general.yesAction'),
    negativeText: $t('general.noAction'),
    positiveButtonProps,
    negativeButtonProps,
    autoFocus: false,
    closable: false,
    onPositiveClick: async () => {
      const { error } = await POST('/layers/{id}/propose', {
        params: { path: { id: layer.id } },
      });
      if (!error) {
        message.success($t('dataLayers.msgProposed', { title: layer.title }));
      } else {
        message.error($t('errors.unexpected'), error);
      }
      load();
      filters.value = initialFilters();
    },
  });
}

function handleUnproposeClick(layer: AnyLayerRead) {
  dialog.warning({
    title: $t('general.warning'),
    content: $t('dataLayers.warnUnpropose'),
    positiveText: $t('general.yesAction'),
    negativeText: $t('general.noAction'),
    positiveButtonProps,
    negativeButtonProps,
    autoFocus: false,
    closable: false,
    onPositiveClick: async () => {
      const { error } = await POST('/layers/{id}/unpropose', {
        params: { path: { id: layer.id } },
      });
      if (!error) {
        message.success($t('dataLayers.msgUnproposed', { title: layer.title }));
      } else {
        message.error($t('errors.unexpected'), error);
      }
      load();
      filters.value = initialFilters();
    },
  });
}

function handlePublishClick(layer: AnyLayerRead) {
  dialog.warning({
    title: $t('general.warning'),
    content: $t('dataLayers.warnPublish') + ' ' + $t('general.areYouSureHelpTextHint'),
    positiveText: $t('general.yesAction'),
    negativeText: $t('general.noAction'),
    positiveButtonProps,
    negativeButtonProps,
    autoFocus: false,
    closable: false,
    onPositiveClick: async () => {
      const { error } = await POST('/layers/{id}/publish', {
        params: { path: { id: layer.id } },
      });
      if (!error) {
        message.success($t('dataLayers.msgPublished', { title: layer.title }));
      } else {
        message.error($t('errors.unexpected'), error);
      }
      load();
      filters.value = initialFilters();
    },
  });
}

function handleUnpublishClick(layer: AnyLayerRead) {
  dialog.warning({
    title: $t('general.warning'),
    content: $t('dataLayers.warnUnpublish'),
    positiveText: $t('general.yesAction'),
    negativeText: $t('general.noAction'),
    positiveButtonProps,
    negativeButtonProps,
    autoFocus: false,
    closable: false,
    onPositiveClick: async () => {
      const { error } = await POST('/layers/{id}/unpublish', {
        params: { path: { id: layer.id } },
      });
      if (!error) {
        message.success($t('dataLayers.msgUnpublished', { title: layer.title }));
      } else {
        message.error($t('errors.unexpected'), error);
      }
      load();
      filters.value = initialFilters();
    },
  });
}

function handleEditClick(layer: AnyLayerRead) {
  router.push({ name: 'dataLayerEdit', params: { text: state.text?.slug, id: layer.id } });
}

function handleDeleteClick(layer: AnyLayerRead) {
  dialog.warning({
    title: $t('general.warning'),
    content: $t('dataLayers.warnDelete'),
    positiveText: $t('general.yesAction'),
    negativeText: $t('general.noAction'),
    positiveButtonProps,
    negativeButtonProps,
    autoFocus: false,
    closable: false,
    onPositiveClick: async () => {
      const { error } = await DELETE('/layers/{id}', {
        params: { path: { id: layer.id } },
      });
      if (!error) {
        message.success($t('dataLayers.msgDeleted', { title: layer.title }));
        // remove from browsable layers
        browse.layers = browse.layers.filter((l) => l.id !== layer.id);
      } else {
        message.error($t('errors.unexpected'), error);
      }
      load();
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
    {{ $t('dataLayers.heading') }} {{ layers ? `(${layers?.length})` : '' }}
    <HelpButtonWidget help-key="dataLayersView" />
  </IconHeading>

  <template v-if="layers && !error && !loading">
    <!-- Filters -->
    <n-collapse
      style="margin-bottom: var(--layout-gap)"
      @item-header-click="handleFilterCollapseItemClick"
    >
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
          <n-checkbox v-model:checked="filters.public" :label="$t('dataLayers.public')" />
          <n-checkbox v-model:checked="filters.notPublic" :label="$t('dataLayers.notPublic')" />
          <n-checkbox v-model:checked="filters.proposed" :label="$t('dataLayers.proposed')" />
          <n-checkbox v-model:checked="filters.notProposed" :label="$t('dataLayers.notProposed')" />
          <n-checkbox v-model:checked="filters.ownedByMe" :label="$t('dataLayers.ownedByMe')" />
          <n-checkbox
            v-model:checked="filters.ownedByOthers"
            :label="$t('dataLayers.ownedByOthers')"
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
    <!-- Layers List -->
    <div class="content-block">
      <template v-if="paginatedData.length > 0">
        <n-list style="background-color: transparent">
          <layer-list-item
            v-for="item in paginatedData"
            :key="item.id"
            :target-layer="item"
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
    :description="$t('init.loading')"
  />

  <div v-else>
    {{ $t('errors.error') }}
  </div>
</template>
