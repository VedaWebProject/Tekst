<script setup lang="ts">
import { ref } from 'vue';
import { useStateStore, type BrowseLocation } from '@/stores';
import { NButton, NModal, NSelect, NFormItem, NForm, type SelectOption } from 'naive-ui';
import KeyboardArrowLeftRound from '@vicons/material/KeyboardArrowLeftRound';
import KeyboardArrowRightRound from '@vicons/material/KeyboardArrowRightRound';
import MenuBookOutlined from '@vicons/material/MenuBookOutlined';

interface LevelLocationModel {
  loading: boolean;
  location: BrowseLocation;
  options?: SelectOption[];
}

const state = useStateStore();
const showModal = ref(false);
const locationModel = ref<LevelLocationModel[]>(
  state.text?.levels.map((lvl, i) => ({
    loading: false,
    location: {
      label: lvl,
      level: i,
      position: 0,
    },
  })) || []
);

function updateOptions(updatedLevel: number) {
  console.log('Update options. Updated level: ' + updatedLevel);
}

function handleSearch(q: string, level: number) {
  locationModel.value[level].loading = true;
  setTimeout(() => {
    locationModel.value[level].options = [
      {
        label: 'foo',
        value: '87fd9d87gdf8g',
      },
      {
        label: 'bar',
        value: 'rtre6576ret5re76',
      },
    ];
    locationModel.value[level].loading = false;
  }, 800);
}
</script>

<template>
  <!-- text location toolbar buttons -->
  <div class="text-location">
    <n-button secondary title="Previous location" size="large" color="#fffe">
      <template #icon>
        <KeyboardArrowLeftRound />
      </template>
    </n-button>
    <n-button
      secondary
      title="Select location"
      @click="showModal = true"
      size="large"
      color="#fffe"
    >
      <template #icon>
        <MenuBookOutlined />
      </template>
    </n-button>
    <n-button secondary title="Next location" size="large" color="#fffe">
      <template #icon>
        <KeyboardArrowRightRound />
      </template>
    </n-button>
  </div>

  <!-- text location selector modal -->
  <n-modal
    v-model:show="showModal"
    preset="card"
    embedded
    :closable="false"
    size="huge"
    style="width: 600px; max-width: 95%"
  >
    <h2>Select location</h2>
    <n-form
      :model="locationModel"
      label-placement="left"
      label-width="auto"
      size="large"
      require-mark-placement="right-hanging"
    >
      <n-form-item
        v-for="(levelLoc, index) in locationModel"
        :label="levelLoc.location.label"
        :key="`${index}_${levelLoc.location.label}`"
      >
        <n-select
          v-model:value="levelLoc.location.id"
          :options="levelLoc.options"
          filterable
          :placeholder="levelLoc.location.label"
          :loading="levelLoc.loading"
          remote
          @search="(q) => handleSearch(q, levelLoc.location.level)"
          @update:value="() => updateOptions(levelLoc.location.level)"
        />
      </n-form-item>
    </n-form>
    <div>{{ locationModel }}</div>
    <div style="text-align: right">
      <n-button type="primary">Select</n-button>
    </div>
  </n-modal>
</template>

<style scoped>
.text-location {
  display: flex;
  justify-content: space-between;
  gap: 0.75rem;
}
</style>
