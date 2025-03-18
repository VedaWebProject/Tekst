<script setup lang="ts">
import { PATCH, resourceTypes, type PlatformStateUpdate } from '@/api';
import { dynInputCreateBtnProps } from '@/common';
import FormSectionHeading from '@/components/FormSectionHeading.vue';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import LabeledSwitch from '@/components/LabeledSwitch.vue';
import { useMessages } from '@/composables/messages';
import { useModelChanges } from '@/composables/modelChanges';
import { usePlatformData } from '@/composables/platformData';
import DynamicInputControls from '@/forms/DynamicInputControls.vue';
import { platformSettingsFormRules } from '@/forms/formRules';
import TranslationFormItem from '@/forms/TranslationFormItem.vue';
import { $t, localeProfiles } from '@/i18n';
import { SettingsIcon } from '@/icons';
import { useStateStore } from '@/stores';
import { cloneDeep } from 'lodash-es';
import {
  NButton,
  NDivider,
  NDynamicInput,
  NFlex,
  NForm,
  NFormItem,
  NInput,
  NSelect,
  NTabPane,
  NTabs,
  type FormInst,
  type TabsInst,
} from 'naive-ui';
import { computed, ref, watch } from 'vue';

const state = useStateStore();
const { loadPlatformData } = usePlatformData();
const { message } = useMessages();

const tabsRef = ref<TabsInst>();

const getFormModel = (): PlatformStateUpdate =>
  cloneDeep(state.pf?.state || ({} as PlatformStateUpdate));

const loading = ref(false);
const formRef = ref<FormInst | null>(null);
const formModel = ref<PlatformStateUpdate>(getFormModel());

const { changed, reset, getChanges } = useModelChanges(formModel);

const defaultTextOptions = state.pf?.texts.map((t) => ({
  label: t.title,
  value: t.id,
}));

const localeOptions = computed(() =>
  localeProfiles.map((lp) => ({ label: `${lp.icon} ${lp.displayFull}`, value: lp.key }))
);

const oskFontOptions = computed(
  () => state.pf?.state.fonts.map((f) => ({ label: f, value: f })) || []
);

const resourceTypeOptions = computed(
  () =>
    resourceTypes.map((rt) => ({
      label: $t(`resources.types.${rt.name}.label`),
      value: rt.name,
    })) || []
);

async function handleSaveClick() {
  loading.value = true;
  formRef.value
    ?.validate(async (validationError) => {
      if (validationError) return;
      const { error } = await PATCH('/platform/state', {
        body: getChanges() as PlatformStateUpdate,
      });
      if (!error) {
        await loadPlatformData();
        // If the current locale is invalid after updating the settings,
        // this call will fix it!
        await state.setLocale(state.locale);
        message.success($t('admin.platformSettings.msgSaved'), undefined, 10);
      } else {
        resetForm();
      }
      reset();
      loading.value = false;
    })
    .catch(() => {
      message.error($t('errors.followFormRules'));
      reset();
      loading.value = false;
    });
}

function resetForm() {
  formModel.value = getFormModel();
  reset();
  formRef.value?.restoreValidation();
}

watch(
  () => state.locale,
  () => {
    setTimeout(() => {
      tabsRef.value?.syncBarPosition();
    }, 100);
  }
);
</script>

<template>
  <icon-heading level="1" :icon="SettingsIcon">
    {{ $t('general.settings') }}
    <help-button-widget help-key="adminSettingsView" />
  </icon-heading>

  <div class="content-block">
    <n-form
      ref="formRef"
      :model="formModel"
      :rules="platformSettingsFormRules"
      :disabled="loading"
      label-placement="top"
      label-width="auto"
      require-mark-placement="right-hanging"
    >
      <n-tabs
        ref="tabsRef"
        type="line"
        :placement="state.smallScreen ? 'top' : 'left'"
        :pane-class="state.smallScreen ? 'mt-md' : 'ml-lg'"
      >
        <!-- GENERAL -->
        <n-tab-pane :tab="$t('general.general')" name="general">
          <form-section-heading :label="$t('general.platform')" />

          <!-- PLATFORM TITLE -->
          <n-form-item path="platformName" :label="$t('models.platformSettings.platformName')">
            <n-input
              v-model:value="formModel.platformName"
              type="text"
              :placeholder="$t('models.platformSettings.platformName')"
              @keydown.enter.prevent
            />
          </n-form-item>

          <!-- PLATFORM DESCRIPTION -->
          <translation-form-item
            v-model="formModel.platformSubtitle"
            parent-form-path-prefix="platformSubtitle"
            :loading="loading"
            :main-form-label="$t('models.platformSettings.platformSubtitle')"
            :translation-form-label="$t('models.platformSettings.platformSubtitle')"
            :translation-form-rules="platformSettingsFormRules.platformSubtitleTranslation"
          />

          <!-- DEFAULT TEXT -->
          <n-form-item path="defaultTextId" :label="$t('models.platformSettings.defaultText')">
            <n-select
              v-model:value="formModel.defaultTextId"
              clearable
              :options="defaultTextOptions"
              :placeholder="$t('admin.platformSettings.defaultTextPlaceholder')"
              :consistent-menu-width="false"
              @keydown.enter.prevent
            />
          </n-form-item>

          <!-- INTERNATIONALIZATION -->
          <form-section-heading :label="$t('admin.platformSettings.headingI18n')" />

          <!-- AVAILABLE LOCALES -->
          <n-form-item
            path="availableLocales"
            :label="$t('models.platformSettings.availableLocales')"
            required
          >
            <n-select
              v-model:value="formModel.availableLocales"
              multiple
              max-tag-count="responsive"
              :options="localeOptions"
              :placeholder="$t('models.platformSettings.availableLocales')"
              :consistent-menu-width="false"
              @keydown.enter.prevent
            />
          </n-form-item>
        </n-tab-pane>

        <!-- NAVIGATION -->
        <n-tab-pane :tab="$t('admin.platformSettings.nav.heading')" name="navigation">
          <form-section-heading :label="$t('admin.platformSettings.nav.aliasSearch')" />

          <n-form-item :show-label="false" :show-feedback="false">
            <!-- DIRECT JUMP ON UNIQUE ALIAS SEARCH -->
            <labeled-switch
              v-model="formModel.directJumpOnUniqueAliasSearch"
              :label="$t('models.platformSettings.directJumpOnUniqueAliasSearch')"
            />
          </n-form-item>

          <form-section-heading :label="$t('admin.platformSettings.nav.customNavLabels')" />

          <!-- CUSTOM MAIN NAV BROWSE ENTRY -->
          <translation-form-item
            v-model="formModel.navBrowseEntry"
            parent-form-path-prefix="navBrowseEntry"
            :loading="loading"
            :main-form-label="$t('models.platformSettings.navBrowseEntry')"
            :translation-form-label="$t('models.platformSettings.navBrowseEntry')"
            :translation-form-rules="platformSettingsFormRules.navEntryTranslation"
          />

          <!-- CUSTOM MAIN NAV SEARCH ENTRY -->
          <translation-form-item
            v-model="formModel.navSearchEntry"
            parent-form-path-prefix="navSearchEntry"
            :loading="loading"
            :main-form-label="$t('models.platformSettings.navSearchEntry')"
            :translation-form-label="$t('models.platformSettings.navSearchEntry')"
            :translation-form-rules="platformSettingsFormRules.navEntryTranslation"
          />

          <!-- CUSTOM MAIN NAV INFO ENTRY -->
          <translation-form-item
            v-model="formModel.navInfoEntry"
            parent-form-path-prefix="navInfoEntry"
            :loading="loading"
            :main-form-label="$t('models.platformSettings.navInfoEntry')"
            :translation-form-label="$t('models.platformSettings.navInfoEntry')"
            :translation-form-rules="platformSettingsFormRules.navEntryTranslation"
          />
        </n-tab-pane>

        <!-- BROWSE VIEW -->
        <n-tab-pane :tab="$t('admin.platformSettings.headingBrowseView')" name="browseView">
          <form-section-heading :label="$t('admin.platformSettings.headingBrowseView')" />
          <n-flex vertical>
            <!-- SHOW RESOURCE CATEGORY HEADINGS -->
            <labeled-switch
              v-model="formModel.showResourceCategoryHeadings"
              :label="$t('models.platformSettings.showResourceCategoryHeadings')"
            />
            <!-- PRIORITIZE BROWSE LEVEL RESOURCES -->
            <labeled-switch
              v-model="formModel.prioritizeBrowseLevelResources"
              :label="$t('models.platformSettings.prioritizeBrowseLevelResources')"
            />
            <!-- SHOW LOCATION ALIASES IN BROWSE VIEW -->
            <labeled-switch
              v-model="formModel.showLocationAliases"
              :label="$t('models.platformSettings.showLocationAliases')"
            />
          </n-flex>
        </n-tab-pane>

        <!-- RESOURCES -->
        <n-tab-pane :tab="$t('resources.heading')" name="resources">
          <!-- DENY RESOURCE TYPES -->
          <form-section-heading :label="$t('admin.platformSettings.headingRestrictedResTypes')" />
          <n-form-item :label="$t('models.platformSettings.denyResourceTypes')">
            <n-select
              v-model:value="formModel.denyResourceTypes"
              multiple
              clearable
              max-tag-count="responsive"
              :options="resourceTypeOptions"
              placeholder="–"
            />
          </n-form-item>

          <!-- ADDITIONAL FONTS -->
          <form-section-heading
            :label="$t('models.platformSettings.fonts')"
            help-key="adminSettingsResourceFonts"
          />
          <n-form-item v-if="formModel.fonts" :show-label="false">
            <n-dynamic-input
              v-model:value="formModel.fonts"
              show-sort-button
              :min="0"
              :max="64"
              :create-button-props="dynInputCreateBtnProps"
              @create="() => ''"
            >
              <template #default="{ index }">
                <n-form-item
                  ignore-path-change
                  :label="$t('general.name')"
                  :path="`fonts[${index}]`"
                  :rule="platformSettingsFormRules.fontName"
                  style="flex: 2"
                >
                  <n-input
                    v-model:value="formModel.fonts[index]"
                    :placeholder="$t('general.name')"
                    @keydown.enter.prevent
                  />
                </n-form-item>
              </template>
              <template #action="{ index, create, remove }">
                <dynamic-input-controls
                  top-offset
                  :movable="false"
                  :insert-disabled="(formModel.fonts.length || 0) >= 64"
                  @remove="() => remove(index)"
                  @insert="() => create(index)"
                />
              </template>
              <template #create-button-default>
                {{ $t('general.addAction') }}
              </template>
            </n-dynamic-input>
          </n-form-item>

          <!-- OSK -->
          <form-section-heading
            :label="$t('models.platformSettings.oskModes')"
            help-key="adminSettingsOskModes"
          />
          <n-form-item v-if="formModel.oskModes" :show-label="false">
            <n-dynamic-input
              v-model:value="formModel.oskModes"
              show-sort-button
              :min="0"
              :max="64"
              :create-button-props="dynInputCreateBtnProps"
              @create="() => ({ key: '', name: '', font: '' })"
            >
              <template #default="{ index }">
                <div
                  style="
                    display: flex;
                    align-items: flex-start;
                    gap: 12px;
                    flex: 2;
                    flex-wrap: wrap;
                  "
                >
                  <n-form-item
                    ignore-path-change
                    :label="$t('general.key')"
                    :path="`oskModes[${index}].key`"
                    :rule="platformSettingsFormRules.oskModeKey"
                  >
                    <n-input
                      v-model:value="formModel.oskModes[index].key"
                      :placeholder="$t('general.key')"
                      @keydown.enter.prevent
                    />
                  </n-form-item>
                  <n-form-item
                    ignore-path-change
                    :label="$t('general.name')"
                    :path="`oskModes[${index}].name`"
                    :rule="platformSettingsFormRules.oskModeName"
                    style="flex: 2"
                  >
                    <n-input
                      v-model:value="formModel.oskModes[index].name"
                      :placeholder="$t('general.name')"
                      @keydown.enter.prevent
                    />
                  </n-form-item>
                  <n-form-item
                    v-if="!!oskFontOptions.length"
                    ignore-path-change
                    :path="`oskModes[${index}].font`"
                    :label="$t('models.platformSettings.oskModeFont')"
                  >
                    <n-select
                      v-model:value="formModel.oskModes[index].font"
                      clearable
                      :options="oskFontOptions"
                      :placeholder="$t('general.default')"
                      :consistent-menu-width="false"
                      style="min-width: 200px"
                      @keydown.enter.prevent
                    />
                  </n-form-item>
                </div>
              </template>
              <template #action="{ index, create, remove, move }">
                <dynamic-input-controls
                  top-offset
                  :move-up-disabled="index === 0"
                  :move-down-disabled="index === formModel.oskModes.length - 1"
                  :insert-disabled="(formModel.fonts?.length || 0) >= 64"
                  @move-up="() => move('up', index)"
                  @move-down="() => move('down', index)"
                  @remove="() => remove(index)"
                  @insert="() => create(index)"
                />
              </template>
              <template #create-button-default>
                {{ $t('general.addAction') }}
              </template>
            </n-dynamic-input>
          </n-form-item>
        </n-tab-pane>

        <!-- SEARCH -->
        <n-tab-pane :tab="$t('routes.pageTitle.search')" name="search">
          <form-section-heading :label="$t('routes.pageTitle.search')" />

          <!-- INDEX UNPUBLISHED RESOURCES -->
          <n-form-item :show-label="false">
            <labeled-switch
              v-model="formModel.indexUnpublishedResources"
              :label="$t('models.platformSettings.indexUnpublishedResources')"
            />
          </n-form-item>
        </n-tab-pane>

        <!-- BRANDING -->
        <n-tab-pane :tab="$t('admin.platformSettings.headingBranding')" name="branding">
          <form-section-heading :label="$t('admin.platformSettings.headingBranding')" />

          <n-flex vertical class="mb-lg">
            <!-- SHOW LOGO ON LOADING SCREEN -->
            <labeled-switch
              v-model="formModel.showLogoOnLoadingScreen"
              :label="$t('models.platformSettings.showLogoOnLoadingScreen')"
            />
            <!-- SHOW LOGO IN HEADER -->
            <labeled-switch
              v-model="formModel.showLogoInHeader"
              :label="$t('models.platformSettings.showLogoInHeader')"
            />
            <!-- SHOW TEKST FOOTER HINT -->
            <labeled-switch
              v-model="formModel.showTekstFooterHint"
              :label="$t('models.platformSettings.showTekstFooterHint')"
            />
          </n-flex>
        </n-tab-pane>
      </n-tabs>
    </n-form>

    <n-divider />

    <button-shelf>
      <n-button secondary :disabled="!changed" @click="resetForm">{{
        $t('general.resetAction')
      }}</n-button>
      <n-button type="primary" :disabled="!changed" @click="handleSaveClick">{{
        $t('general.saveAction')
      }}</n-button>
    </button-shelf>
  </div>
</template>
