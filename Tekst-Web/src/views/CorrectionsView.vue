<script setup lang="ts">
import HugeLabelledIcon from '@/components/generic/HugeLabelledIcon.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import CorrectionListItem from '@/components/resource/CorrectionListItem.vue';
import { $t } from '@/i18n';
import { ArrowBackIcon, CorrectionNoteIcon, NoContentIcon } from '@/icons';
import { useResourcesStore, useStateStore } from '@/stores';
import { pickTranslation } from '@/utils';
import { NButton, NIcon, NList } from 'naive-ui';
import { computed, onBeforeMount } from 'vue';
import { onBeforeRouteUpdate, RouterLink, useRouter } from 'vue-router';

const props = defineProps<{
  textSlug?: string;
  resId: string;
}>();

const state = useStateStore();
const resources = useResourcesStore();
const router = useRouter();

const resourceId = computed(() => props.resId);
const resource = computed(() => resources.ofText.find((r) => r.id === resourceId.value));
const resourceTitle = computed(() => pickTranslation(resource.value?.title, state.locale));

// change route if text changes
onBeforeRouteUpdate((to, from) => {
  if (to.params.textSlug !== from.params.textSlug) {
    router.push({ name: 'resources', params: { textSlug: to.params.textSlug } });
  }
});

onBeforeMount(async () => {
  await resources.loadCorrections(props.resId);
});
</script>

<template>
  <icon-heading level="1" :icon="CorrectionNoteIcon">
    {{ $t('corrections.heading', { title: resourceTitle }) }}
  </icon-heading>

  <router-link :to="{ name: 'resources', params: { textSlug: props.textSlug } }">
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
