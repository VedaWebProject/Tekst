<script setup lang="ts">
import {
  GET,
  type AnyResourceRead,
  type LocationRead,
  type ResourceSearchQuery,
  type SearchableResourceType,
} from '@/api';
import { dynInputCreateBtnProps } from '@/common';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import LocationRange from '@/components/search/LocationRange.vue';
import { useMessages } from '@/composables/messages';
import CommonSearchFormItems from '@/forms/resources/search/CommonSearchFormItems.vue';
import SearchOccurrenceSelector from '@/forms/resources/search/SearchOccurrenceSelector.vue';
import { resourceTypeSearchForms } from '@/forms/resources/search/mappings';
import GeneralSearchSettingsForm from '@/forms/search/GeneralSearchSettingsForm.vue';
import { $t } from '@/i18n';
import { AddIcon, ClearIcon, LevelsIcon, NoContentIcon, ResourceIcon, SearchIcon } from '@/icons';
import { useResourcesStore, useSearchStore, useStateStore, useThemeStore } from '@/stores';
import { pickTranslation } from '@/utils';
import { useMagicKeys, whenever } from '@vueuse/core';
import {
  NButton,
  NDynamicInput,
  NEmpty,
  NFlex,
  NForm,
  NFormItem,
  NIcon,
  NSelect,
  NTag,
  type FormInst,
} from 'naive-ui';
import type { SelectMixedOption, SelectOption } from 'naive-ui/es/select/src/interface';
import { computed, h, ref, watch, watchEffect, type VNodeChild } from 'vue';

interface AdvancedSearchFormModelItem extends ResourceSearchQuery {
  resource?: AnyResourceRead;
}
interface AdvancedSearchFormModel {
  queries: AdvancedSearchFormModelItem[];
}

const state = useStateStore();
const theme = useThemeStore();
const search = useSearchStore();
const resources = useResourcesStore();
const { message } = useMessages();

const formModel = ref<AdvancedSearchFormModel>({ queries: [] });
const formRef = ref<FormInst | null>(null);

const searchHeading = computed(
  () => pickTranslation(state.pf?.state.navSearchEntry, state.locale) || $t('common.search')
);

const resourceOptions = computed(() => {
  const textIds = [
    ...(state.text?.id ? [state.text?.id] : []),
    ...(state.pf?.texts.map((t) => t.id).filter((tId) => tId !== state.text?.id) || []),
  ];
  return textIds.map((tId) => ({
    type: 'group',
    render: () =>
      h(
        'div',
        {
          class: 'text-small b',
          style: {
            color: theme.getAccentColors(tId).base,
            padding: '8px',
          },
        },
        state.textById(tId)?.title || ''
      ),
    key: tId,
    children: resources.all
      .filter((r) => r.textId === tId)
      .filter((r) => r.config.general.searchableAdv)
      .sort((a, b) => {
        const categories =
          state.pf?.texts.find((t) => t.id === a.textId)?.resourceCategories?.map((c) => c.key) ||
          [];
        const catA = categories.includes(a.config.general.category || '')
          ? categories.indexOf(a.config.general.category || '')
          : 99;
        const catB = categories.includes(b.config.general.category || '')
          ? categories.indexOf(b.config.general.category || '')
          : 99;
        const soA = a.config.general.sortOrder || 99;
        const soB = b.config.general.sortOrder || 99;
        return catA * 100 + soA - (catB * 100 + soB);
      })
      .map((r) => ({
        label: pickTranslation(r.title, state.locale),
        value: r.id,
        resourceType: r.resourceType,
        textColor: theme.getAccentColors(tId).base,
        level: r.level,
        textId: r.textId,
      })),
  }));
});

const resourceColors = computed(() =>
  Object.fromEntries(resources.all.map((r) => [r.id, { colors: theme.getAccentColors(r.textId) }]))
);

const queriesCommonText = computed(() =>
  !!formModel.value.queries.length &&
  formModel.value.queries.map((q) => q.resource?.textId).every((val, _, arr) => val === arr[0])
    ? formModel.value.queries[0].resource?.textId
    : undefined
);
const queriesCommonLevel = computed(() =>
  !!formModel.value.queries.length &&
  formModel.value.queries.map((q) => q.resource?.level).every((val, _, arr) => val === arr[0])
    ? formModel.value.queries[0].resource?.level
    : undefined
);
const locRangeEnabled = computed(
  () => !!queriesCommonText.value && queriesCommonLevel.value !== undefined
);
const locRangeExpanded = ref(false);
const fromLocationPath = ref<LocationRead[]>([]);
const toLocationPath = ref<LocationRead[]>([]);

watchEffect(async () => {
  locRangeExpanded.value = false;
  if (!locRangeEnabled.value) {
    fromLocationPath.value = [];
    toLocationPath.value = [];
    return;
  }
  const { data, error } = await GET('/locations/first-last-paths', {
    params: { query: { txt: queriesCommonText.value as string, lvl: queriesCommonLevel.value } },
  });
  if (!error) {
    fromLocationPath.value = data[0];
    toLocationPath.value = data[1];
  }
});

function renderResourceOptionLabel(option: SelectOption): VNodeChild {
  return h(NFlex, { align: 'center', wrap: false, class: 'mr-lg' }, () => [
    !state.smallScreen && h(NIcon, { component: ResourceIcon, color: option.textColor as string }),
    h('div', { style: 'white-space: nowrap' }, option.label as string),
    h('div', { style: 'flex: 2' }),
    !state.smallScreen &&
      h(
        NTag,
        { size: 'small', style: 'cursor: pointer; font-weight: normal' },
        {
          default: () => state.getTextLevelLabel(option.textId as string, option.level as number),
          icon: () => h(NIcon, { component: LevelsIcon }),
        }
      ),
  ]);
}

function handleResourceChange(
  resQueryIndex: number,
  resId: string,
  resType: SearchableResourceType
) {
  if (!formModel.value.queries[resQueryIndex]) return;
  if (formModel.value.queries[resQueryIndex].cmn.res !== resId) {
    formModel.value.queries[resQueryIndex] = {
      cmn: { res: resId, occ: formModel.value.queries[resQueryIndex].cmn.occ || 'must' },
      rts: { type: resType },
      resource: resources.all.find((r) => r.id === resId),
    };
  }
}

function getNewSearchItem(): AdvancedSearchFormModelItem | undefined {
  const resId =
    resourceOptions.value.find((ro) => ro.key === state.text?.id)?.children[0]?.value ||
    resources.ofText[0]?.id;
  const resource =
    resources.all.find((r) => r.id === resId) || resources.ofText[0] || resources.all[0];
  if (!resource) return undefined;
  return {
    cmn: { res: resource.id, occ: 'must' },
    rts: { type: resource.resourceType as SearchableResourceType },
    resource: resource,
  };
}

function addSearchItem(index: number) {
  const newItem = getNewSearchItem();
  if (!newItem) return;
  formModel.value.queries.splice(index + 1, 0, newItem);
}

function removeSearchItem(index: number) {
  formModel.value.queries.splice(index, 1);
}

function handleSearch() {
  formRef.value
    ?.validate(async (validationError) => {
      if (validationError) return;
      // constrain location range (or don't)
      if (locRangeEnabled.value && locRangeExpanded.value) {
        const lvl = fromLocationPath.value.length - 1;
        search.settingsAdvanced.rng = {
          lvl,
          from: fromLocationPath.value[lvl].position,
          to: toLocationPath.value[lvl].position,
        };
      } else {
        delete search.settingsAdvanced.rng;
      }
      search.searchAdvanced(
        formModel.value.queries.map((q) => {
          const { resource, ...query } = q; // remove "resource" prop from q
          return query;
        })
      );
    })
    .catch(() => {
      message.error($t('errors.followFormRules'));
    });
}

function initQueries() {
  if (search.currentRequest?.type === 'advanced') {
    formModel.value.queries = search.currentRequest.q.map((q) => ({
      ...q,
      resource: resources.all.find((r) => r.id === q.cmn.res),
    }));
  } else {
    const searchItem = getNewSearchItem();
    formModel.value.queries = !!searchItem ? [searchItem] : [];
  }
}

watch(
  () => resources.dataHash,
  () => {
    initQueries();
  },
  { immediate: true }
);

// search on Ctrl+Enter
const keys = useMagicKeys();
const ctrlEnter = keys['Ctrl+Enter'];
whenever(ctrlEnter, () => {
  handleSearch();
});
</script>

<template>
  <icon-heading level="1" :icon="SearchIcon">
    {{ searchHeading }}
    <help-button-widget help-key="searchView" />
  </icon-heading>

  <general-search-settings-form />

  <n-form
    v-if="!!resources.all.length"
    ref="formRef"
    :model="formModel"
    label-placement="top"
    label-width="auto"
    require-mark-placement="right-hanging"
  >
    <n-dynamic-input
      v-model:value="formModel.queries"
      :min="1"
      :max="32"
      item-class="search-item my-md"
      :create-button-props="dynInputCreateBtnProps"
      @create="getNewSearchItem"
    >
      <!-- SEARCH ITEM -->
      <template #default="{ value: query, index: queryIndex }">
        <div
          class="content-block"
          :style="{ borderLeft: `8px solid ${resourceColors[query.cmn.res].colors.base}` }"
        >
          <n-flex align="center" :wrap="false" class="mb-lg">
            <n-flex align="flex-start" style="flex: 2">
              <n-form-item :show-label="false" :show-feedback="false" style="flex: 6 400px">
                <n-select
                  class="search-resource-select b"
                  :value="query.cmn.res"
                  :options="resourceOptions"
                  :consistent-menu-width="false"
                  :menu-props="{ class: 'search-resource-select-menu' }"
                  :render-label="renderResourceOptionLabel"
                  @update:value="
                    (v, o: SelectMixedOption) =>
                      handleResourceChange(queryIndex, v, o.resourceType as SearchableResourceType)
                  "
                />
              </n-form-item>
              <search-occurrence-selector
                v-model:occurrence="query.cmn.occ"
                :query-index="queryIndex"
                style="flex: 1 180px"
              />
            </n-flex>
            <n-button
              v-if="formModel.queries.length > 1"
              quaternary
              circle
              :title="$t('common.remove')"
              :focusable="false"
              class="action-button-remove"
              @click="removeSearchItem(queryIndex)"
            >
              <n-icon :component="ClearIcon" />
            </n-button>
          </n-flex>
          <div>
            <component
              :is="resourceTypeSearchForms[query.rts.type]"
              v-model="query.rts"
              :resource="query.resource"
              :query-index="queryIndex"
            />
            <common-search-form-items v-model:comment="query.cmn.cmt" :query-index="queryIndex" />
          </div>
        </div>
        <n-button
          v-if="
            formModel.queries.length < 32 &&
            queryIndex === formModel.queries.length - 1 &&
            !!resourceOptions.length
          "
          secondary
          :title="$t('common.insert')"
          :focusable="false"
          class="mt-lg"
          @click="addSearchItem(queryIndex)"
        >
          <template #icon>
            <n-icon :component="AddIcon" />
          </template>
          {{ $t('search.advancedSearch.addQuery') }}
        </n-button>
      </template>
      <!-- ADD / REMOVE ACTION BUTTONS -->
      <template #action>
        <!-- this is needed so the default action buttons don't show :( -->
        <div></div>
      </template>
    </n-dynamic-input>

    <!-- LOCATION RANGE -->
    <location-range
      v-model:from-path="fromLocationPath"
      v-model:to-path="toLocationPath"
      v-model:expanded="locRangeExpanded"
      :enabled="locRangeEnabled"
    />
  </n-form>
  <n-empty v-else :description="$t('search.advancedSearch.msgNoResources')">
    <template #icon>
      <n-icon :component="NoContentIcon" />
    </template>
  </n-empty>

  <button-shelf v-if="!!resources.all.length" top-gap>
    <n-button
      type="primary"
      :title="`${$t('common.searchAction')} (${$t('common.ctrlEnter')})`"
      :disabled="!formModel.queries.length"
      @click.stop.prevent="handleSearch"
    >
      {{ $t('common.searchAction') }}
    </n-button>
  </button-shelf>
</template>

<style scoped>
:deep(.search-item) {
  position: relative;
  flex-direction: column;
  margin: 1rem 0;
}

:deep(.search-item > .content-block) {
  margin: 0;
}
</style>

<style>
.search-resource-select-menu.n-base-select-menu
  .n-base-select-option.n-base-select-option--selected,
.search-resource-select-menu.n-base-select-menu
  .n-base-select-option.n-base-select-option--selected
  .n-base-select-option__check {
  font-weight: bold;
}

.search-resource-select-menu .n-base-select-option .n-base-select-option__content {
  width: 100%;
}
</style>
