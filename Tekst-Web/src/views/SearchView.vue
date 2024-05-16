<script setup lang="ts">
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import { AddIcon, ClearIcon, NoContentIcon, SearchIcon } from '@/icons';
import { resourceTypeSearchForms } from '@/forms/resources/search/mappings';
import {
  NCollapse,
  NCollapseItem,
  NForm,
  NButton,
  NDynamicInput,
  NIcon,
  NSelect,
  NFormItem,
  useThemeVars,
  type FormInst,
} from 'naive-ui';
import { computed, h, ref, watch } from 'vue';
import type { AdvancedSearchRequestBody, AnyResourceRead, ResourceType } from '@/api';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import HugeLabelledIcon from '@/components/generic/HugeLabelledIcon.vue';
import type { SelectMixedOption } from 'naive-ui/es/select/src/interface';
import CommonSearchFormItems from '@/forms/resources/search/CommonSearchFormItems.vue';
import { $t } from '@/i18n';
import { useRouter } from 'vue-router';
import { useResourcesStore, useSearchStore, useStateStore } from '@/stores';
import GeneralSearchSettingsForm from '@/forms/search/GeneralSearchSettingsForm.vue';
import { useMessages } from '@/composables/messages';
import { pickTranslation } from '@/utils';

type AdvancedSearchRequestQuery = AdvancedSearchRequestBody['q'][number];
interface AdvancedSearchFormModelItem extends AdvancedSearchRequestQuery {
  resource?: AnyResourceRead;
}
interface AdvancedSearchFormModel {
  queries: AdvancedSearchFormModelItem[];
}

const state = useStateStore();
const search = useSearchStore();
const resources = useResourcesStore();
const router = useRouter();
const themeVars = useThemeVars();
const { message } = useMessages();

const formModel = ref<AdvancedSearchFormModel>({ queries: [] });
const formRef = ref<FormInst | null>(null);

const resourceOptions = computed(() =>
  resources.ofText.map((r) => ({
    label: `${pickTranslation(r.title, state.locale)} (${$t('resources.types.' + r.resourceType + '.label')})`,
    value: r.id,
    resourceType: r.resourceType,
  }))
);

function handleResourceChange(resQueryIndex: number, resId: string, resType: ResourceType) {
  if (!formModel.value.queries[resQueryIndex]) return;
  if (formModel.value.queries[resQueryIndex].cmn.res !== resId) {
    formModel.value.queries[resQueryIndex] = {
      cmn: { res: resId, opt: true },
      rts: { type: resType },
      resource: resources.ofText.find((r) => r.id === resId),
    };
  }
}

function getNewSearchItem(): AdvancedSearchFormModelItem {
  return {
    cmn: { res: resources.ofText[0].id, opt: true },
    rts: { type: resources.ofText[0].resourceType },
    resource: resources.ofText[0],
  };
}

function addSearchItem(index: number) {
  formModel.value.queries.splice(index + 1, 0, getNewSearchItem());
}

function removeSearchItem(index: number) {
  formModel.value.queries.splice(index, 1);
}

function handleSearch(e: UIEvent) {
  e.preventDefault();
  e.stopPropagation();
  formRef.value
    ?.validate(async (validationError) => {
      if (validationError) return;
      router.push({
        name: 'searchResults',
        query: {
          q: search.encodeQueryParam({
            type: 'advanced',
            q: formModel.value.queries.map((q) => {
              // eslint-disable-next-line @typescript-eslint/no-unused-vars
              const { resource, ...query } = q; // remove "resource" q
              return query;
            }),
            gen: search.settingsGeneral,
            adv: search.settingsAdvanced,
          }),
        },
      });
    })
    .catch(() => {
      message.error($t('errors.followFormRules'));
    });
}

function initQueries() {
  if (search.lastReq?.type === 'advanced') {
    formModel.value.queries = search.lastReq.q.map((q) => ({
      ...q,
      resource: resources.ofText.find((r) => r.id === q.cmn.res),
    }));
  } else {
    formModel.value.queries = resources.ofText.length ? [getNewSearchItem()] : [];
  }
}

function renderResourceOptionLabel(option: SelectMixedOption) {
  return h('span', { style: { color: 'var(--accent-color)' } }, { default: () => option.label });
}

watch(
  () => resources.ofTextHash,
  () => {
    initQueries();
  },
  { immediate: true }
);
</script>

<template>
  <icon-heading level="1" :icon="SearchIcon">
    {{ $t('search.heading') }}
    <help-button-widget help-key="searchView" />
  </icon-heading>

  <n-collapse>
    <n-collapse-item :title="$t('search.settings.heading')" name="settings">
      <div class="gray-box" style="margin-bottom: var(--layout-gap)">
        <general-search-settings-form />
      </div>
    </n-collapse-item>
  </n-collapse>

  <n-form
    v-if="!!resources.ofText.length"
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
      item-class="advanced-search-item"
      item-style="flex-direction: column; margin: 0"
      @create="getNewSearchItem"
    >
      <!-- SEARCH ITEM -->
      <template #default="{ value: query, index: queryIndex }">
        <div style="flex-grow: 2" class="search-item content-block">
          <n-form-item :show-label="false" style="flex-grow: 2">
            <n-select
              :value="query.cmn.res"
              :options="resourceOptions"
              :consistent-menu-width="false"
              :render-label="renderResourceOptionLabel"
              style="font-weight: var(--font-weight-bold)"
              @update:value="
                (v, o: SelectMixedOption) =>
                  handleResourceChange(queryIndex, v, o.resourceType as ResourceType)
              "
            />
          </n-form-item>
          <component
            :is="resourceTypeSearchForms[query.rts.type]"
            v-model="query.rts"
            :resource="query.resource"
            :query-index="queryIndex"
          />
          <common-search-form-items
            v-model:comment="query.cmn.cmt"
            v-model:optional="query.cmn.opt"
            :query-index="queryIndex"
          />
          <div class="search-item-action-buttons">
            <n-button
              v-if="formModel.queries.length < 32"
              circle
              :color="themeVars.bodyColor"
              :style="{ color: themeVars.textColor1 }"
              :title="$t('general.insertAction')"
              :focusable="false"
              class="action-button-insert"
              @click="addSearchItem(queryIndex)"
            >
              <n-icon :component="AddIcon" />
            </n-button>
            <n-button
              v-if="formModel.queries.length > 1"
              circle
              :color="themeVars.bodyColor"
              :style="{ color: themeVars.textColor1 }"
              :title="$t('general.removeAction')"
              :focusable="false"
              class="action-button-remove"
              @click="removeSearchItem(queryIndex)"
            >
              <n-icon :component="ClearIcon" />
            </n-button>
          </div>
        </div>
      </template>
      <!-- ADD / REMOVE ACTION BUTTONS -->
      <template #action>
        <div>
          <!-- this is needed so the default action buttons don't show -->
        </div>
      </template>
    </n-dynamic-input>
  </n-form>

  <huge-labelled-icon
    v-else
    :message="$t('search.advancedSearch.msgNoResources')"
    :icon="NoContentIcon"
  />

  <button-shelf v-if="!!resources.ofText.length" top-gap>
    <n-button type="primary" :disabled="!formModel.queries.length" @click="handleSearch">
      {{ $t('search.searchAction') }}
    </n-button>
  </button-shelf>
</template>

<style scoped>
.search-item {
  position: relative;
}

.search-item-action-buttons {
  position: absolute;
  left: 0;
  bottom: -16px;
  width: 100%;
  display: flex;
  flex-wrap: nowrap;
  justify-content: center;
  gap: var(--layout-gap);
}
.search-item-action-buttons .action-button-insert:hover {
  color: var(--col-success) !important;
}
.search-item-action-buttons .action-button-remove:hover {
  color: var(--col-error) !important;
}
.search-item-action-button-wrapper {
  border-radius: 3px;
}
</style>
