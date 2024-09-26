<script setup lang="ts">
import { computed, ref } from 'vue';
import NInputOsk from '@/components/NInputOsk.vue';
import { useRouter } from 'vue-router';
import { useResourcesStore, useSearchStore, useStateStore, useThemeStore } from '@/stores';
import { NButton, NIcon, NPopselect, type InputInst, type SelectOption } from 'naive-ui';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import GenericModal from '@/components/generic/GenericModal.vue';
import { SettingsIcon, SearchIcon, ResourceIcon } from '@/icons';
import GeneralSearchSettingsForm from '@/forms/search/GeneralSearchSettingsForm.vue';
import QuickSearchSettingsForm from '@/forms/search/QuickSearchSettingsForm.vue';
import { GET } from '@/api';
import { $t } from '@/i18n';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import { usePlatformData } from '@/composables/platformData';

const emit = defineEmits(['submit']);

const state = useStateStore();
const theme = useThemeStore();
const { pfData } = usePlatformData();
const search = useSearchStore();
const resources = useResourcesStore();
const router = useRouter();

const showLocationSelect = ref(false);
const showSettingsModal = ref(false);
const showTargetResourcesModal = ref(false);
const searchInput = ref<string>('');
const loading = ref(false);
const quickSearchInputRef = ref<InputInst | null>(null);

const locationSelectOptions = ref<SelectOption[]>([]);

const searchableResources = computed(
  () =>
    (search.settingsQuick.txt?.length
      ? search.settingsQuick.txt
      : pfData.value?.texts.map((t) => t.id)
    )?.map((tId) => ({
      title: pfData.value?.texts.find((t) => t.id === tId)?.title,
      color: theme.getAccentColors(tId).base,
      resources: resources.all.filter((r) => r.textId === tId && r.config?.common?.quickSearchable),
    })) || []
);

async function handleSearch() {
  loading.value = true;
  const matchesToShow = 10;

  // check if the input matches a location alias
  const { data, error } = await GET('/locations/by-alias', {
    params: {
      query: { txt: state.text?.id || '', alias: searchInput.value, limit: matchesToShow },
    },
  });

  if (!error && !!data.length) {
    if (data.length === 1 && !!pfData.value?.state.directJumpOnUniqueAliasSearch) {
      // there is one matching location alias, so we directly navigate to this location
      router.push({
        name: 'browse',
        params: { text: state.text?.slug || '' },
        query: { lvl: data[0].level, pos: data[0].position },
      });
    } else {
      // there are multiple matching locations, so we show a list of them
      locationSelectOptions.value = [
        {
          type: 'group',
          label: $t('browse.location.goTo'),
          children: [
            ...data.map((l) => ({
              type: 'location',
              label: l.label + (l.full ? ` (${l.full})` : ''),
              value: l.id,
              level: l.level,
              position: l.position,
            })),
            ...(data.length === matchesToShow
              ? [
                  {
                    label: '...',
                    value: '...',
                    disabled: true,
                  },
                ]
              : []),
          ],
        },
        {
          type: 'group',
          label: $t('search.searchAction'),
          children: [
            {
              type: 'search',
              label: searchInput.value,
              value: searchInput.value,
            },
          ],
        },
      ];
      showLocationSelect.value = true;
    }
  } else {
    // there is no matching location alias, so we perform a quick search using the input
    quickSearch(searchInput.value);
  }

  loading.value = false;

  if (!state.smallScreen) {
    quickSearchInputRef.value?.select();
  } else {
    quickSearchInputRef.value?.blur();
  }
}

function handleSelect(value: string, option: SelectOption) {
  if (option.type === 'location') {
    router.push({
      name: 'browse',
      params: { text: state.text?.slug || '' },
      query: { lvl: option.level as number, pos: option.position as number },
    });
    emit('submit', searchInput.value);
  } else if (option.type === 'search') {
    quickSearch(value);
  }
  showLocationSelect.value = false;
  locationSelectOptions.value = [];
}

function quickSearch(q: string) {
  router.push({
    name: 'searchResults',
    query: {
      q: search.encodeQueryParam({
        type: 'quick',
        q,
        gen: search.settingsGeneral,
        qck: search.settingsQuick,
      }),
    },
  });
  emit('submit', searchInput.value);
}
</script>

<template>
  <div v-bind="$attrs">
    <n-popselect
      trigger="manual"
      :show="showLocationSelect"
      :options="locationSelectOptions"
      width="trigger"
      @update:value="handleSelect"
      @clickoutside="showLocationSelect = false"
    >
      <n-input-osk
        ref="quickSearchInputRef"
        v-model="searchInput"
        round
        :placeholder="$t('search.quickSearch.title')"
        :max-length="512"
        :loading="loading"
        @input="showLocationSelect = false"
        @keydown.enter.stop.prevent="handleSearch"
      >
        <template #prefix>
          <n-icon :component="SearchIcon" />
        </template>
        <template #suffix>
          <n-button
            text
            :title="$t('general.settings')"
            :focusable="false"
            @click.stop.prevent="
              () => {
                quickSearchInputRef?.blur();
                showSettingsModal = true;
              }
            "
          >
            <template #icon>
              <n-icon :component="SettingsIcon" />
            </template>
          </n-button>
          <help-button-widget help-key="quickSearch" @click="quickSearchInputRef?.blur()" />
        </template>
      </n-input-osk>
    </n-popselect>
  </div>

  <generic-modal
    v-model:show="showSettingsModal"
    :title="`${$t('search.quickSearch.title')}: ${$t('general.settings')}`"
    :icon="SettingsIcon"
  >
    <quick-search-settings-form @target-resources-click="showTargetResourcesModal = true" />
    <general-search-settings-form />

    <button-shelf>
      <n-button type="primary" @click="showSettingsModal = false">
        {{ $t('general.okAction') }}
      </n-button>
    </button-shelf>
  </generic-modal>

  <generic-modal
    v-model:show="showTargetResourcesModal"
    :title="$t('search.settings.quick.targetResources')"
    :icon="ResourceIcon"
    width="wide"
  >
    <template v-for="(txt, index) in searchableResources" :key="`${txt.title}_${index}`">
      <h3 :style="{ color: txt.color }">{{ txt.title }}</h3>
      <ul class="m-0">
        <li v-for="res in txt.resources" :key="res.id">
          {{ resources.resourceTitles[res.id] }}
        </li>
      </ul>
    </template>
  </generic-modal>
</template>
