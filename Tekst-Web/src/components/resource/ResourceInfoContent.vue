<script setup lang="ts">
import { type AnyResourceRead } from '@/api';
import CollapsibleContent from '@/components/CollapsibleContent.vue';
import CopyToClipboardButton from '@/components/generic/CopyToClipboardButton.vue';
import HydratedHtml from '@/components/generic/HydratedHtml.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import TranslationDisplay from '@/components/generic/TranslationDisplay.vue';
import MetadataDisplay from '@/components/resource/MetadataDisplay.vue';
import ResourceCoverageWidget from '@/components/resource/ResourceCoverageWidget.vue';
import ResourceInfoTags from '@/components/resource/ResourceInfoTags.vue';
import UserDisplay from '@/components/user/UserDisplay.vue';
import env from '@/env';
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
const resInfoUrl = computed(
  () =>
    `${origin}${env.WEB_PATH_STRIPPED}/texts/${state.text?.slug || '???'}/resources#id=${props.resource.id}`
);
const showInfoModal = ref(false);
</script>

<template>
  <div>
    <n-flex justify="flex-end" align="center" class="mb-lg" style="flex-wrap: wrap-reverse">
      <!-- SUBTITLE -->
      <span v-if="resource.subtitle.length" style="flex: 2">
        <translation-display :value="resource.subtitle" />
      </span>
      <resource-info-tags :resource="resource" />
    </n-flex>

    <n-flex justify="flex-end" align="center" class="mb-lg" style="flex-wrap: wrap-reverse">
      <user-display
        v-if="!!auth.user"
        :user="resource.owners || undefined"
        size="small"
        :system="resource.public"
        style="flex: 2"
      />
      <copy-to-clipboard-button
        v-if="state.text"
        tertiary
        size="tiny"
        :text="resInfoUrl"
        :title="$t('resources.copyInfoUrlTip')"
        show-msg
      >
        {{ $t('resources.copyInfoUrl') }}
      </copy-to-clipboard-button>
    </n-flex>

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
