<script setup lang="ts">
import { type AnyResourceRead } from '@/api';
import CollapsibleContent from '@/components/CollapsibleContent.vue';
import HydratedHtml from '@/components/generic/HydratedHtml.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import TranslationDisplay from '@/components/generic/TranslationDisplay.vue';
import MetadataDisplay from '@/components/resource/MetadataDisplay.vue';
import ResourceCoverageWidget from '@/components/resource/ResourceCoverageWidget.vue';
import ResourceInfoTags from '@/components/resource/ResourceInfoTags.vue';
import UserDisplay from '@/components/user/UserDisplay.vue';
import {
  CoverageIcon,
  DescIcon,
  FormatQuoteIcon,
  LinkIcon,
  MetadataIcon,
  SiteNoticeIcon,
} from '@/icons';
import { useAuthStore, useStateStore } from '@/stores';
import { pickTranslation } from '@/utils';
import { NFlex, NIcon } from 'naive-ui';
import { computed, ref } from 'vue';

const props = defineProps<{
  resource: AnyResourceRead;
}>();

const auth = useAuthStore();
const state = useStateStore();

const descriptionHtml = computed(() => pickTranslation(props.resource.description, state.locale));
const showInfoModal = ref(false);
</script>

<template>
  <div>
    <n-flex class="mb-lg">
      <!-- SUBTITLE -->
      <span v-if="resource.subtitle.length">
        <translation-display :value="resource.subtitle" />
      </span>
      <resource-info-tags
        :resource="resource"
        reverse
        style="flex: 2; justify-content: flex-start"
      />
    </n-flex>

    <user-display
      v-if="!!auth.user"
      :user="resource.owner || undefined"
      size="small"
      :system="resource.public"
    />

    <!-- DESCRIPTION -->
    <div class="gray-box" v-if="!!descriptionHtml">
      <icon-heading level="3" :icon="DescIcon">
        {{ $t('common.description') }}
      </icon-heading>
      <collapsible-content>
        <hydrated-html
          :html="descriptionHtml"
          :style="{ fontFamily: resource.contentFont }"
          class="text-medium"
        />
      </collapsible-content>
    </div>

    <!-- METADATA -->
    <div class="gray-box" v-if="resource.meta && Object.keys(resource.meta).length">
      <icon-heading level="3" :icon="MetadataIcon">
        {{ $t('models.meta.modelLabel') }}
      </icon-heading>
      <metadata-display :data="resource.meta" class="text-medium" />
    </div>

    <!-- CITATION -->
    <div class="gray-box" v-if="resource.citation">
      <icon-heading level="3" :icon="FormatQuoteIcon">
        {{ $t('browse.contents.widgets.infoWidget.citeAs') }}
      </icon-heading>
      <div :style="{ fontFamily: resource.contentFont }" class="text-medium">
        {{ resource.citation }}
      </div>
    </div>

    <!-- COVERAGE -->
    <div class="gray-box">
      <icon-heading level="3" :icon="CoverageIcon">
        {{ $t('browse.contents.widgets.infoWidget.coverage') }}
      </icon-heading>
      <resource-coverage-widget :resource="resource" @navigate="showInfoModal = false" />
    </div>

    <!-- LICENSE -->
    <div class="gray-box">
      <icon-heading level="3" :icon="SiteNoticeIcon">
        {{ $t('models.resource.license') }}
      </icon-heading>
      <template v-if="resource.license || resource.licenseUrl">
        <a
          v-if="resource.licenseUrl"
          :href="resource.licenseUrl"
          target="_blank"
          rel="noopener noreferrer"
        >
          <n-flex align="center" size="small">
            <n-icon :component="LinkIcon" />
            <span>{{ resource.license || resource.licenseUrl }}</span>
          </n-flex>
        </a>
        <span v-else>
          {{ resource.license }}
        </span>
      </template>
      <i v-else>
        {{ $t('browse.contents.widgets.infoWidget.noLicense') }}
      </i>
    </div>
  </div>
</template>
