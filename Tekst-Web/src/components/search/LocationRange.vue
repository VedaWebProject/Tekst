<script setup lang="ts">
import { type LocationRead } from '@/api';
import LocationSelectForm from '@/forms/LocationSelectForm.vue';
import { $t } from '@/i18n';
import { ArrowForwardIcon, ErrorIcon } from '@/icons';
import { NCollapse, NCollapseItem, NEmpty, NFlex, NIcon, NTag } from 'naive-ui';
import { computed, ref, watchEffect } from 'vue';

defineProps<{
  enabled?: boolean;
}>();

const fromPath = defineModel<LocationRead[]>('fromPath', { default: [] });
const toPath = defineModel<LocationRead[]>('toPath', { default: [] });
const expanded = defineModel<boolean>('expanded');

const fromLocationFullLabel = computed(() => fromPath.value.map((loc) => loc.label).join(', '));
const toLocationFullLabel = computed(() => toPath.value.map((loc) => loc.label).join(', '));
const rangeExpandedNames = ref<string[]>(expanded.value ? ['range'] : []);

watchEffect(() => {
  rangeExpandedNames.value = expanded.value ? ['range'] : [];
});

function handleExpandedChange(names: string[]) {
  if (names.includes('range')) {
    rangeExpandedNames.value = ['range'];
    expanded.value = true;
  } else {
    rangeExpandedNames.value = [];
    expanded.value = false;
  }
}
</script>

<template>
  <div class="gray-box">
    <n-collapse :expanded-names="rangeExpandedNames" @update:expanded-names="handleExpandedChange">
      <n-collapse-item name="range">
        <template #header>
          <n-flex align="center" size="small">
            {{ $t('search.advancedSearch.range.title') }}:&nbsp;
            <n-flex v-if="enabled && !!rangeExpandedNames.length" align="center" size="small">
              <n-tag size="small">{{ fromLocationFullLabel }}</n-tag>
              <n-icon :component="ArrowForwardIcon" />
              <n-tag size="small">{{ toLocationFullLabel }}</n-tag>
            </n-flex>
            <template v-else>
              <n-tag size="small">{{ $t('search.advancedSearch.range.unconstrained') }}</n-tag>
            </template>
          </n-flex>
        </template>
        <n-flex v-if="enabled" size="large" align="stretch">
          <div style="flex: 2 320px">
            <div class="mb-sm">{{ $t('common.from') }} ...</div>
            <location-select-form v-model="fromPath" :allow-level-change="false" />
          </div>
          <div style="flex: 2 320px">
            <div class="mb-sm">{{ $t('common.to') }} ...</div>
            <location-select-form v-model="toPath" :allow-level-change="false" />
          </div>
        </n-flex>
        <n-empty v-else :description="$t('search.advancedSearch.range.msgImpossible')">
          <template #icon>
            <n-icon :component="ErrorIcon" />
          </template>
        </n-empty>
      </n-collapse-item>
    </n-collapse>
  </div>
</template>
