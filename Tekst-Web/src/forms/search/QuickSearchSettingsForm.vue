<script setup lang="ts">
import LabeledSwitch from '@/components/LabeledSwitch.vue';
import { InfoIcon } from '@/icons';
import { useSearchStore, useStateStore } from '@/stores';
import { NButton, NForm, NFormItem, NIcon, NSelect } from 'naive-ui';
import { computed } from 'vue';

const emit = defineEmits(['targetResourcesClick']);

const search = useSearchStore();
const state = useStateStore();

const textOptions = computed(() => state.pf?.texts.map((t) => ({ label: t.title, value: t.id })));
</script>

<template>
  <n-form :model="search.settingsQuick">
    <!-- DEFAULT OPERATOR -->
    <n-form-item :show-label="false" :show-feedback="false">
      <labeled-switch
        v-model="search.settingsQuick.op"
        on-value="AND"
        off-value="OR"
        :label="$t('search.settings.quick.defaultOperator')"
        :disabled="search.settingsQuick.re"
      />
    </n-form-item>

    <!-- REGEXP -->
    <n-form-item :show-label="false" :show-feedback="false">
      <labeled-switch
        v-model="search.settingsQuick.re"
        :label="$t('search.settings.quick.regexp')"
        @update:model-value="(v) => v && (search.settingsQuick.op = 'OR')"
      />
    </n-form-item>

    <!-- MATCH NATIVE CONTENTS ONLY -->
    <n-form-item :show-label="false" :show-feedback="false">
      <labeled-switch
        v-model="search.settingsQuick.inh"
        :label="$t('search.settings.quick.inheritedContents')"
      />
    </n-form-item>

    <!-- ONLY FIND LOCATIONS ON TEXT'S DEFAULT LEVEL -->
    <n-form-item :show-label="false" :show-feedback="false">
      <labeled-switch
        v-model="search.settingsQuick.allLvls"
        :label="$t('search.settings.quick.allLevels')"
      />
    </n-form-item>

    <!-- TEXTS -->
    <n-form-item
      v-if="(state.pf?.texts.length || 0) > 1"
      path="txt"
      :label="$t('common.text', 2)"
      class="mt-lg"
    >
      <n-select
        v-model:value="search.settingsQuick.txt"
        :options="textOptions"
        :placeholder="$t('search.settings.quick.textsPlaceholder')"
        clearable
        multiple
      >
        <template #action>
          <n-button text size="small" :focusable="false" @click="emit('targetResourcesClick')">
            <template #icon>
              <n-icon :component="InfoIcon" />
            </template>
            {{ $t('search.settings.quick.targetResources') }}
          </n-button>
        </template>
      </n-select>
    </n-form-item>
  </n-form>
</template>
