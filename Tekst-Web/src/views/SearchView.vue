<script setup lang="ts">
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import { AddIcon, MinusIcon, NoContentIcon, SearchIcon } from '@/icons';
import { resourceTypeSearchForms } from '@/forms/resources/search/mappings';
import { NForm, NButton, NDynamicInput, NIcon, NSelect, NFormItem } from 'naive-ui';
import { computed, ref, watch } from 'vue';
import type { AdvancedSearchRequestBody, ResourceType, SearchRequestBody } from '@/api';
import { useResourcesStore, useStateStore } from '@/stores';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import HugeLabelledIcon from '@/components/generic/HugeLabelledIcon.vue';
import type { SelectMixedOption } from 'naive-ui/es/select/src/interface';
import CommonSearchFormItems from '@/forms/resources/search/CommonSearchFormItems.vue';
import { $t } from '@/i18n';
import { useRouter } from 'vue-router';
import { Base64 } from 'js-base64';

const state = useStateStore();
const resources = useResourcesStore();
const router = useRouter();
const queries = ref<AdvancedSearchRequestBody['q']>([]);

const resourceOptions = computed(() =>
  resources.data.map((r) => ({
    label: `${r.title} (${$t('resources.types.' + r.resourceType + '.label')})`,
    value: r.id,
    resourceType: r.resourceType,
  }))
);

function handleResourceChange(resQueryIndex: number, resId: string, resType: ResourceType) {
  if (!queries.value[resQueryIndex]) return;
  if (queries.value[resQueryIndex].res !== resId) {
    queries.value[resQueryIndex] = {
      res: resId,
      type: resType,
    };
  }
}

function getNewSearchItem() {
  return {
    res: resources.data[0].id,
    type: resources.data[0].resourceType,
  };
}

function addSearchItem(index: number) {
  queries.value.splice(index + 1, 0, getNewSearchItem());
}

function removeSearchItem(index: number) {
  queries.value.splice(index, 1);
}

function handleSearch(e: UIEvent) {
  e.preventDefault();
  e.stopPropagation();
  const reqBody: SearchRequestBody = {
    type: 'advanced',
    q: queries.value,
    gen: state.searchSettingsGeneral,
    adv: state.searchSettingsAdvanced,
  };
  console.log(reqBody);
  router.push({
    name: 'searchResults',
    params: {
      req: Base64.encode(JSON.stringify(reqBody), true),
    },
  });
}

watch(
  () => resources.data,
  () => {
    queries.value = [];
  }
);
</script>

<template>
  <icon-heading level="1" :icon="SearchIcon">
    {{ $t('search.heading') }}
    <help-button-widget help-key="searchView" />
  </icon-heading>

  <div class="content-block">
    <n-form v-if="!!resources.data.length">
      <n-dynamic-input
        v-model:value="queries"
        :min="1"
        :max="64"
        item-class="dynamic-input-item"
        @create="getNewSearchItem"
      >
        <!-- SEARCH ITEM -->
        <template #default="{ value: resourceQuery, index }">
          <div
            style="display: flex; gap: var(--layout-gap); flex-wrap: nowrap; width: 100%"
            :style="{ flexDirection: state.smallScreen ? 'column' : 'row' }"
          >
            <div style="flex-grow: 2">
              <n-form-item :label="$t('search.advancedSearch.targetResource')">
                <n-select
                  :value="resourceQuery.res"
                  :options="resourceOptions"
                  :consistent-menu-width="false"
                  @update:value="
                    (v, o: SelectMixedOption) =>
                      handleResourceChange(index, v, o.resourceType as ResourceType)
                  "
                />
              </n-form-item>
              <component
                :is="resourceTypeSearchForms[resourceQuery.type]"
                v-model:value="queries[index]"
              />
              <common-search-form-items
                v-model:comment="queries[index].cmt"
                v-model:required="queries[index].req"
              />
            </div>
            <div
              style="display: flex; gap: var(--layout-gap)"
              :style="{
                flexDirection: state.smallScreen ? 'row' : 'column',
                padding: state.smallScreen ? '0 0 0.25rem 0' : 'var(--layout-gap) 0',
              }"
            >
              <n-button
                secondary
                type="primary"
                :title="$t('general.removeAction')"
                :disabled="queries.length <= 1"
                style="flex-grow: 2"
                @click="removeSearchItem(index)"
              >
                <template #icon>
                  <n-icon :component="MinusIcon" />
                </template>
              </n-button>
              <n-button
                secondary
                type="primary"
                :title="$t('general.insertAction')"
                :disabled="queries.length >= 64"
                style="flex-grow: 2"
                @click="addSearchItem(index)"
              >
                <template #icon>
                  <n-icon :component="AddIcon" />
                </template>
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
        <!-- "CREATE INITIAL ITEM" BUTTON -->
        <template #create-button-default>
          {{ $t('search.advancedSearch.btnAddSearchItem') }}
        </template>
      </n-dynamic-input>
    </n-form>

    <huge-labelled-icon
      v-else
      :message="$t('search.advancedSearch.msgNoResources')"
      :icon="NoContentIcon"
    />

    <button-shelf v-if="!!resources.data.length" top-gap>
      <n-button type="primary" :disabled="!queries.length" @click="handleSearch">
        {{ $t('search.searchAction') }}
      </n-button>
    </button-shelf>
  </div>
</template>

<style>
.dynamic-input-item:not(:first-child) {
  border-top: 1px solid var(--main-bg-color);
  padding: var(--content-gap) 0;
}
</style>
