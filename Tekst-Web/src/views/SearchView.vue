<script setup lang="ts">
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import { ClearIcon, NoContentIcon, SearchIcon } from '@/icons';
import { resourceTypeSearchForms } from '@/forms/resources/search/mappings';
import { NForm, NButton, NDynamicInput, NIcon, NSelect, NFormItem } from 'naive-ui';
import { computed, ref, watch } from 'vue';
import type { AdvancedSearchRequestBody, ResourceType } from '@/api';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import HugeLabelledIcon from '@/components/generic/HugeLabelledIcon.vue';
import type { SelectMixedOption } from 'naive-ui/es/select/src/interface';
import CommonSearchFormItems from '@/forms/resources/search/CommonSearchFormItems.vue';
import { $t } from '@/i18n';
import { useRouter } from 'vue-router';
import InsertItemSeparator from '@/components/InsertItemSeparator.vue';
import { useResourcesStore, useSearchStore } from '@/stores';

const search = useSearchStore();
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
  if (queries.value[resQueryIndex].cmn.res !== resId) {
    queries.value[resQueryIndex] = {
      cmn: { res: resId, opt: true },
      rts: { ...queries.value[resQueryIndex].rts, type: resType },
    };
  }
}

function getNewSearchItem(): AdvancedSearchRequestBody['q'][number] {
  return {
    cmn: { res: resources.data[0].id, opt: true },
    rts: { type: resources.data[0].resourceType },
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
  router.push({
    name: 'searchResults',
    query: {
      q: search.encodeQueryParam({
        type: 'advanced',
        q: queries.value,
        gen: search.settingsGeneral,
        adv: search.settingsAdvanced,
      }),
    },
  });
}

function initQueries() {
  if (search.lastReq?.type === 'advanced') {
    queries.value = search.lastReq.q;
  } else {
    queries.value = resources.data.length ? [getNewSearchItem()] : [];
  }
}

watch(
  () => resources.data,
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

  <n-form
    v-if="!!resources.data.length"
    :model="queries"
    label-placement="top"
    label-width="auto"
    require-mark-placement="right-hanging"
  >
    <n-dynamic-input
      v-model:value="queries"
      :min="1"
      :max="32"
      item-class="advanced-search-item"
      item-style="flex-direction: column; margin: 0"
      @create="getNewSearchItem"
    >
      <!-- SEARCH ITEM -->
      <template #default="{ value: resourceQuery, index }">
        <div style="flex-grow: 2" class="content-block">
          <div style="display: flex; gap: 0.5rem">
            <n-form-item :show-label="false" style="flex-grow: 2">
              <n-select
                :value="resourceQuery.cmn.res"
                :options="resourceOptions"
                :consistent-menu-width="false"
                size="large"
                @update:value="
                  (v, o: SelectMixedOption) =>
                    handleResourceChange(index, v, o.resourceType as ResourceType)
                "
              />
            </n-form-item>
            <n-button
              class="btn-search-item-remove"
              style="padding: 0.5rem"
              quaternary
              size="large"
              :title="$t('general.removeAction')"
              :disabled="queries.length <= 1"
              @click="removeSearchItem(index)"
            >
              <template #icon>
                <n-icon :component="ClearIcon" />
              </template>
            </n-button>
          </div>
          <component
            :is="resourceTypeSearchForms[resourceQuery.rts.type]"
            v-model:value="resourceQuery.rts"
          />
          <common-search-form-items
            v-model:comment="resourceQuery.cmn.cmt"
            v-model:optional="resourceQuery.cmn.opt"
          />
        </div>
        <insert-item-separator
          :title="$t('general.insertAction')"
          :disabled="queries.length >= 32"
          @click="addSearchItem(index)"
        />
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

  <button-shelf v-if="!!resources.data.length">
    <n-button type="primary" :disabled="!queries.length" @click="handleSearch">
      {{ $t('search.searchAction') }}
    </n-button>
  </button-shelf>
</template>
