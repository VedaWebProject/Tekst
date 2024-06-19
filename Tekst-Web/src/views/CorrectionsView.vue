<script setup lang="ts">
import IconHeading from '@/components/generic/IconHeading.vue';
import { ArrowBackIcon, CorrectionNoteIcon, DeleteIcon, NoContentIcon } from '@/icons';
import { $t } from '@/i18n';
import { useResourcesStore, useStateStore } from '@/stores';
import { computed, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { pickTranslation, utcToLocalTime } from '@/utils';
import { NEllipsis, NTable, NButton, NIcon, NTime } from 'naive-ui';
import { RouterLink } from 'vue-router';
import { useMessages } from '@/composables/messages';
import { DELETE } from '@/api';
import HugeLabelledIcon from '@/components/generic/HugeLabelledIcon.vue';
import { onBeforeMount } from 'vue';

const state = useStateStore();
const resources = useResourcesStore();
const route = useRoute();
const router = useRouter();
const { message } = useMessages();

const loading = ref(false);
const resourceId = computed(() => route.params.id.toString());
const resource = computed(() =>
  route.params.id ? resources.ofText.find((r) => r.id === resourceId.value) : undefined
);
const resourceTitle = computed(() => pickTranslation(resource.value?.title, state.locale));

async function deleteCorrection(e: UIEvent, correctionId: string) {
  e.stopPropagation();
  e.preventDefault();
  loading.value = true;
  const { error } = await DELETE('/corrections/{id}', {
    params: { path: { id: correctionId } },
  });
  if (!error) {
    message.success($t('corrections.msgDeleted'));
    if (resource.value && resource.value.corrections) {
      resources.corrections[resourceId.value] = resources.corrections[resourceId.value].filter(
        (c) => c.id !== correctionId
      );
      const res = resources.all.find((r) => r.id === resourceId.value);
      if (res) {
        res.corrections = res.corrections != null ? res.corrections - 1 : 0;
      }
    }
  }
  loading.value = false;
}

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
    <n-table v-if="!!resources.corrections[resourceId]?.length" :bordered="false" single-line>
      <thead>
        <tr>
          <th>Note</th>
          <th>Date</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="correction in resources.corrections[resourceId]"
          :key="correction.id"
          class="correction-item"
        >
          <td style="max-width: 50vw">
            <n-ellipsis :tooltip="false">{{ correction.note }}</n-ellipsis>
          </td>
          <td style="white-space: nowrap">
            <n-time
              v-if="correction.date"
              :time="utcToLocalTime(correction.date)"
              type="datetime"
            />
          </td>
          <td style="text-align: right">
            <n-button
              secondary
              size="small"
              :title="$t('general.deleteAction')"
              :disabled="loading"
              :loading="loading"
              @click="(e) => deleteCorrection(e, correction.id)"
            >
              <template #icon>
                <n-icon :component="DeleteIcon" />
              </template>
            </n-button>
          </td>
        </tr>
      </tbody>
    </n-table>
    <huge-labelled-icon v-else :icon="NoContentIcon" :message="$t('search.nothingFound')" />
  </div>
</template>

<style scoped>
tr.correction-item > td {
  background-color: transparent;
}
tr.correction-item {
  cursor: pointer;
  transition: background-color 0.2s;
}
tr.correction-item:hover {
  background-color: var(--main-bg-color);
}
</style>
