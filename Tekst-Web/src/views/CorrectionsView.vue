<script setup lang="ts">
import IconHeading from '@/components/generic/IconHeading.vue';
import { ArrowBackIcon, CorrectionNoteIcon, NoContentIcon } from '@/icons';
import { $t } from '@/i18n';
import { useResourcesStore, useStateStore } from '@/stores';
import { computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { pickTranslation } from '@/utils';
import { NButton, NIcon, NList } from 'naive-ui';
import { RouterLink } from 'vue-router';
import HugeLabelledIcon from '@/components/generic/HugeLabelledIcon.vue';
import { onBeforeMount } from 'vue';
import CorrectionListItem from '@/components/resource/CorrectionListItem.vue';

const state = useStateStore();
const resources = useResourcesStore();
const route = useRoute();
const router = useRouter();

const resourceId = computed(() => route.params.id.toString());
const resource = computed(() =>
  route.params.id ? resources.ofText.find((r) => r.id === resourceId.value) : undefined
);
const resourceTitle = computed(() => pickTranslation(resource.value?.title, state.locale));

// change route if text changes
watch(
  () => state.text,
  (newText) => {
    router.push({ name: 'resources', params: { text: newText?.slug } });
  }
);

onBeforeMount(async () => {
  await resources.loadCorrections(route.params.id.toString());
});
</script>

<template>
  <icon-heading level="1" :icon="CorrectionNoteIcon">
    {{ $t('corrections.heading', { title: resourceTitle }) }}
  </icon-heading>

  <router-link :to="{ name: 'resources', params: { text: state.text?.slug } }">
    <n-button text :focusable="false">
      <template #icon>
        <n-icon :component="ArrowBackIcon" />
      </template>
      {{ $t('resources.backToOverview') }}
    </n-button>
  </router-link>

  <div class="content-block">
    <n-list
      v-if="resource && !!resources.corrections[resourceId]?.length"
      hoverable
      clickable
      style="background-color: transparent"
    >
      <correction-list-item
        v-for="correction in resources.corrections[resourceId]"
        :key="correction.id"
        :resource="resource"
        :correction="correction"
      />
    </n-list>
    <huge-labelled-icon v-else :icon="NoContentIcon" :message="$t('search.nothingFound')" />
  </div>
</template>

<style scoped>
.disabled {
  opacity: 0.5;
  cursor: not-allowed !important;
}
</style>
