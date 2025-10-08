<script setup lang="ts">
import {
  colorPresets,
  PATCH,
  resourceTypes,
  type PlatformStateRead,
  type PlatformStateUpdate,
} from '@/api';
import { dynInputCreateBtnProps } from '@/common';
import FormSection from '@/components/FormSection.vue';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import LabeledSwitch from '@/components/LabeledSwitch.vue';
import { useMessages } from '@/composables/messages';
import { useModelChanges } from '@/composables/modelChanges';
import { usePlatformData } from '@/composables/platformData';
import DynamicInputControls from '@/forms/DynamicInputControls.vue';
import { platformSettingsFormRules, resourceSettingsFormRules } from '@/forms/formRules';
import TranslationFormItem from '@/forms/TranslationFormItem.vue';
import { $t, localeProfiles } from '@/i18n';
import { SettingsIcon } from '@/icons';
import { useStateStore } from '@/stores';
import { cloneDeep } from 'lodash-es';
import {
  NButton,
  NColorPicker,
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
  type SelectOption,
  type TabsInst,
} from 'naive-ui';
import { computed, h, ref, watch } from 'vue';

const state = useStateStore();
const { loadPlatformData } = usePlatformData();
const { message } = useMessages();

const tabsRef = ref<TabsInst>();

const getFormModel = (): PlatformStateRead =>
  cloneDeep(state.pf?.state || ({} as PlatformStateRead));

const loading = ref(false);
const formRef = ref<FormInst | null>(null);
const formModel = ref<PlatformStateRead>(getFormModel());

const { changed, reset, getChanges } = useModelChanges(formModel);

const defaultTextOptions = state.pf?.texts.map((t) => ({
  label: t.title,
  value: t.id,
}));

const localeOptions = computed(() =>
  localeProfiles.map((lp) => ({ label: `${lp.icon} ${lp.displayFull}`, value: lp.key }))
);

const oskFontOptions = computed(() => state.fonts.map((f) => ({ label: f, value: f })) || []);

const resourceTypeOptions = computed(
  () =>
    resourceTypes.map((rt) => ({
      label: $t(`resources.types.${rt.name}.label`),
      value: rt.name,
    })) || []
);

const fontOptions = computed(() =>
  state.fonts.map((f) => ({
    label: f,
    value: f,
  }))
);

function renderFontLabel(option: SelectOption) {
  const fontIsValid = !!option.value && !!state.fonts.includes(option.value as string);
  return h(
    'div',
    {
      style: {
        fontFamily: [option.value, 'var(--font-family-ui)'].filter((f) => !!f).join(', '),
        color: !fontIsValid ? 'var(--error-color)' : undefined,
        textDecoration: !fontIsValid ? 'line-through' : undefined,
      },
    },
    option.label as string
  );
}

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
    {{ $t('common.settings') }}
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
        <n-tab-pane :tab="$t('common.general')" name="general">
          <form-section :title="$t('common.platform')">
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
          </form-section>

          <!-- INTERNATIONALIZATION -->
          <form-section :title="$t('admin.platformSettings.headingI18n')">
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
          </form-section>
        </n-tab-pane>

        <!-- NAVIGATION -->
        <n-tab-pane :tab="$t('admin.platformSettings.nav.heading')" name="navigation">
          <!-- CUSTOM NAV TRANSLATIONS -->
          <form-section :title="$t('admin.platformSettings.nav.customNavLabels')">
            <!-- browse -->
            <translation-form-item
              v-model="formModel.navTranslations.browse"
              parent-form-path-prefix="navTranslations.browse"
              :loading="loading"
              :main-form-label="$t('models.platformSettings.navBrowseEntry')"
              :translation-form-label="$t('models.platformSettings.navBrowseEntry')"
              :translation-form-rules="platformSettingsFormRules.navEntryTranslation"
            />

            <!-- search -->
            <translation-form-item
              v-model="formModel.navTranslations.search"
              parent-form-path-prefix="navTranslations.search"
              :loading="loading"
              :main-form-label="$t('models.platformSettings.navSearchEntry')"
              :translation-form-label="$t('models.platformSettings.navSearchEntry')"
              :translation-form-rules="platformSettingsFormRules.navEntryTranslation"
            />

            <!-- info -->
            <translation-form-item
              v-model="formModel.navTranslations.info"
              parent-form-path-prefix="navTranslations.info"
              :loading="loading"
              :main-form-label="$t('models.platformSettings.navInfoEntry')"
              :translation-form-label="$t('models.platformSettings.navInfoEntry')"
              :translation-form-rules="platformSettingsFormRules.navEntryTranslation"
            />
          </form-section>
        </n-tab-pane>

        <!-- BROWSE VIEW -->
        <n-tab-pane :tab="$t('admin.platformSettings.headingBrowseView')" name="browseView">
          <form-section :title="$t('admin.platformSettings.headingBrowseView')">
            <!-- SHOW RESOURCE CATEGORY HEADINGS -->
            <n-form-item :show-label="false" :show-feedback="false">
              <labeled-switch
                v-model="formModel.showResourceCategoryHeadings"
                :label="$t('models.platformSettings.showResourceCategoryHeadings')"
              />
            </n-form-item>
            <!-- PRIORITIZE BROWSE LEVEL RESOURCES -->
            <n-form-item :show-label="false" :show-feedback="false">
              <labeled-switch
                v-model="formModel.prioritizeBrowseLevelResources"
                :label="$t('models.platformSettings.prioritizeBrowseLevelResources')"
              />
            </n-form-item>
            <!-- SHOW LOCATION ALIASES IN BROWSE VIEW -->
            <n-form-item :show-label="false" :show-feedback="false">
              <labeled-switch
                v-model="formModel.showLocationAliases"
                :label="$t('models.platformSettings.showLocationAliases')"
              />
            </n-form-item>
          </form-section>
        </n-tab-pane>

        <!-- RESOURCES -->
        <n-tab-pane :tab="$t('resources.heading')" name="resources">
          <!-- DENY RESOURCE TYPES -->
          <form-section :title="$t('admin.platformSettings.headingRestrictedResTypes')">
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
          </form-section>

          <!-- OSK -->
          <form-section
            :title="$t('models.platformSettings.oskModes')"
            help-key="adminSettingsOskModes"
          >
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
                      :label="$t('common.key')"
                      :path="`oskModes[${index}].key`"
                      :rule="platformSettingsFormRules.oskModeKey"
                    >
                      <n-input
                        v-model:value="formModel.oskModes[index].key"
                        :placeholder="$t('common.key')"
                        @keydown.enter.prevent
                      />
                    </n-form-item>
                    <n-form-item
                      ignore-path-change
                      :label="$t('common.name')"
                      :path="`oskModes[${index}].name`"
                      :rule="platformSettingsFormRules.oskModeName"
                      style="flex: 2"
                    >
                      <n-input
                        v-model:value="formModel.oskModes[index].name"
                        :placeholder="$t('common.name')"
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
                        :placeholder="$t('common.default')"
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
                  {{ $t('common.add') }}
                </template>
              </n-dynamic-input>
            </n-form-item>
          </form-section>

          <!-- GROUPS -->
          <form-section :title="$t('models.platformSettings.resMetaTranslations')">
            <n-form-item :show-label="false" :show-feedback="false">
              <n-dynamic-input
                v-model:value="formModel.resMetaTranslations"
                show-sort-button
                :max="64"
                :create-button-props="dynInputCreateBtnProps"
                item-class="divided"
                @create="
                  () => ({
                    key: undefined,
                    translations: [{ locale: '*', translation: undefined }],
                  })
                "
              >
                <template #default="{ index }">
                  <n-flex align="flex-start" style="width: 100%">
                    <!-- METADATA KEY -->
                    <n-form-item
                      ignore-path-change
                      :label="$t('common.key')"
                      :path="`resMetaTranslations[${index}].key`"
                      :rule="resourceSettingsFormRules.metaKey"
                      style="flex: 1 200px"
                    >
                      <n-input v-model:value="formModel.resMetaTranslations[index].key" />
                    </n-form-item>
                    <!-- METADATA KEY TRANSLATION -->
                    <translation-form-item
                      v-model="formModel.resMetaTranslations[index].translations"
                      ignore-path-change
                      secondary
                      :parent-form-path-prefix="`resMetaTranslations[${index}].translations`"
                      style="flex: 2 300px"
                      :main-form-label="$t('common.translation')"
                      :translation-form-label="$t('common.translation', 2)"
                      :translation-form-rules="resourceSettingsFormRules.metaValue"
                    />
                  </n-flex>
                </template>
                <template #action="{ index, create, remove, move }">
                  <dynamic-input-controls
                    top-offset
                    :move-up-disabled="index === 0"
                    :move-down-disabled="index === formModel.resMetaTranslations.length - 1"
                    :insert-disabled="formModel.resMetaTranslations.length >= 64"
                    :remove-disabled="formModel.resMetaTranslations.length <= 0"
                    @move-up="() => move('up', index)"
                    @move-down="() => move('down', index)"
                    @remove="() => remove(index)"
                    @insert="() => create(index)"
                  />
                </template>
                <template #create-button-default>
                  {{ $t('common.add') }}
                </template>
              </n-dynamic-input>
            </n-form-item>
          </form-section>
        </n-tab-pane>

        <!-- SEARCH -->
        <n-tab-pane :tab="$t('routes.pageTitle.search')" name="search">
          <form-section :title="$t('routes.pageTitle.search')">
            <!-- INDEX UNPUBLISHED RESOURCES -->
            <n-form-item :show-label="false" :show-feedback="false">
              <labeled-switch
                v-model="formModel.indexUnpublishedResources"
                :label="$t('models.platformSettings.indexUnpublishedResources')"
              />
            </n-form-item>
            <!-- DIRECT JUMP ON UNIQUE ALIAS SEARCH -->
            <n-form-item :show-label="false" :show-feedback="false">
              <labeled-switch
                v-model="formModel.directJumpOnUniqueAliasSearch"
                :label="$t('admin.platformSettings.nav.aliasSearch')"
              />
            </n-form-item>
          </form-section>
        </n-tab-pane>

        <!-- APPEARANCE -->
        <n-tab-pane :tab="$t('admin.platformSettings.headingAppearance')" name="appearance">
          <!-- FONTS -->
          <form-section
            :title="$t('admin.platformSettings.headingFonts')"
            help-key="adminSettingsCustomFonts"
          >
            <!-- custom fonts -->
            <n-form-item
              v-if="formModel.fonts"
              :label="$t('models.platformSettings.fonts')"
              class="parent-form-item"
            >
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
                    :label="$t('common.name')"
                    :path="`fonts[${index}]`"
                    :rule="platformSettingsFormRules.fontName"
                    style="flex: 2"
                  >
                    <n-input
                      v-model:value="formModel.fonts[index]"
                      :placeholder="$t('common.name')"
                      @keydown.enter.prevent
                      :style="{
                        fontFamily: [formModel.fonts[index], 'var(--font-family-ui)']
                          .filter((f) => !!f)
                          .join(', '),
                      }"
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
                  {{ $t('common.add') }}
                </template>
              </n-dynamic-input>
            </n-form-item>

            <!-- ui font -->
            <n-form-item path="uiFont" :label="$t('models.platformSettings.uiFont')">
              <n-select
                v-model:value="formModel.uiFont"
                clearable
                :options="fontOptions"
                :placeholder="$t('common.default')"
                :render-label="renderFontLabel"
              />
            </n-form-item>

            <!-- default content font -->
            <n-form-item path="contentFont" :label="$t('models.platformSettings.contentFont')">
              <n-select
                v-model:value="formModel.contentFont"
                clearable
                :options="fontOptions"
                :placeholder="$t('common.default')"
                :render-label="renderFontLabel"
              />
            </n-form-item>
          </form-section>

          <!-- BRANDING -->
          <form-section :title="$t('admin.platformSettings.headingBranding')">
            <!-- UI COLOR -->
            <n-form-item path="uiColor" :label="$t('models.platformSettings.uiColor')">
              <n-color-picker
                v-model:value="formModel.uiColor"
                :modes="['hex']"
                :show-alpha="false"
                :swatches="colorPresets"
              />
            </n-form-item>
            <!-- SHOW LOGO ON LOADING SCREEN -->
            <n-form-item :show-label="false" :show-feedback="false">
              <labeled-switch
                v-model="formModel.showLogoOnLoadingScreen"
                :label="$t('models.platformSettings.showLogoOnLoadingScreen')"
              />
            </n-form-item>
            <!-- SHOW LOGO IN HEADER -->
            <n-form-item :show-label="false" :show-feedback="false">
              <labeled-switch
                v-model="formModel.showLogoInHeader"
                :label="$t('models.platformSettings.showLogoInHeader')"
              />
            </n-form-item>
            <!-- SHOW TEKST FOOTER HINT -->
            <n-form-item :show-label="false" :show-feedback="false">
              <labeled-switch
                v-model="formModel.showTekstFooterHint"
                :label="$t('models.platformSettings.showTekstFooterHint')"
              />
            </n-form-item>
          </form-section>
        </n-tab-pane>
      </n-tabs>
    </n-form>

    <n-divider />

    <button-shelf>
      <n-button secondary :disabled="!changed" @click="resetForm">{{
        $t('common.reset')
      }}</n-button>
      <n-button type="primary" :disabled="!changed" @click="handleSaveClick">{{
        $t('common.save')
      }}</n-button>
    </button-shelf>
  </div>
</template>
