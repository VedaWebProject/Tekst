<script setup lang="ts">
import LabelledSwitch from '@/components/LabelledSwitch.vue';
import { usePlatformData } from '@/composables/platformData';
import { useSearchStore } from '@/stores';
import { NButton, NFlex, NForm, NFormItem, NSelect } from 'naive-ui';
import { computed } from 'vue';

const emit = defineEmits(['targetResourcesClick']);

const search = useSearchStore();
const { pfData } = usePlatformData();

const textOptions = computed(() =>
  pfData.value?.texts.map((t) => ({ label: t.title, value: t.id }))
);
</script>

<template>
  <n-form :model="search.settingsQuick">
    <!-- TEXTS -->
    <n-form-item
      v-if="(pfData?.texts.length || 0) > 1"
      path="txt"
      :label="$t('search.settings.quick.texts')"
    >
      <n-select
        v-model:value="search.settingsQuick.txt"
        :options="textOptions"
        :placeholder="$t('search.settings.quick.textsPlaceholder')"
        clearable
        multiple
      />
    </n-form-item>

    <n-flex justify="flex-end" class="mb-sm translucent">
      <n-button text size="tiny" class="i" :focusable="false" @click="emit('targetResourcesClick')">
        {{ $t('search.settings.quick.targetResources') }}
      </n-button>
    </n-flex>

    <!-- DEFAULT OPERATOR -->
    <n-form-item path="op" :show-label="false" :show-feedback="false">
      <labelled-switch
        v-model="search.settingsQuick.op"
        checked-value="AND"
        unchecked-value="OR"
        :label="$t('search.settings.quick.defaultOperator')"
        :disabled="search.settingsQuick.re"
      />
    </n-form-item>

    <!-- REGEXP -->
    <n-form-item path="re" :show-label="false" :show-feedback="false">
      <labelled-switch
        v-model="search.settingsQuick.re"
        :label="$t('search.settings.quick.regexp')"
        @update:model-value="(v) => v && (search.settingsQuick.op = 'OR')"
      />
    </n-form-item>
  </n-form>
</template>
