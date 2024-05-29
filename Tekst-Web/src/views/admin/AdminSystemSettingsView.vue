<script setup lang="ts">
import { $t, localeProfiles } from '@/i18n';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import { computed, ref } from 'vue';
import {
  NDynamicInput,
  NDivider,
  NButton,
  NFlex,
  NSelect,
  NForm,
  NFormItem,
  NInput,
  type FormInst,
} from 'naive-ui';
import { usePlatformData } from '@/composables/platformData';
import { PATCH, type PlatformSettingsUpdate } from '@/api';
import { useModelChanges } from '@/composables/modelChanges';
import { useMessages } from '@/composables/messages';
import { platformSettingsFormRules } from '@/forms/formRules';
import TranslationFormItem from '@/forms/TranslationFormItem.vue';
import ButtonShelf from '@/components/generic/ButtonShelf.vue';
import { useStateStore } from '@/stores';
import _cloneDeep from 'lodash.clonedeep';
import { SettingsIcon } from '@/icons';
import LabelledSwitch from '@/components/LabelledSwitch.vue';
import IconHeading from '@/components/generic/IconHeading.vue';
import DynamicInputControls from '@/forms/DynamicInputControls.vue';

const state = useStateStore();
const { pfData, patchPfData } = usePlatformData();
const { message } = useMessages();

const getFormModel = (): PlatformSettingsUpdate => _cloneDeep(pfData.value?.settings || {});

const loading = ref(false);
const formRef = ref<FormInst | null>(null);
const formModel = ref<PlatformSettingsUpdate>(getFormModel());

const { changed, reset, getChanges } = useModelChanges(formModel);

const defaultTextOptions = pfData.value?.texts.map((t) => ({
  label: t.title,
  value: t.id,
}));

const localeOptions = computed(() =>
  localeProfiles.map((lp) => ({ label: `${lp.icon} ${lp.displayFull}`, value: lp.key }))
);

const oskFontOptions = computed(
  () => pfData.value?.settings.customFonts?.map((f) => ({ label: f, value: f })) || []
);

async function handleSaveClick() {
  loading.value = true;
  formRef.value
    ?.validate(async (validationError) => {
      if (validationError) return;
      const { data, error } = await PATCH('/platform/settings', {
        body: getChanges(),
      });
      if (!error) {
        patchPfData({
          settings: data,
        });
        // If the current locale is invalid after updating the settings,
        // this call will fix it!
        await state.setLocale(state.locale);
        message.success(
          $t('admin.system.platformSettings.msgSaved', {
            cacheTTL: pfData.value?.settingsCacheTtl,
          }),
          undefined,
          10
        );
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
</script>

<template>
  <icon-heading level="2" :icon="SettingsIcon">
    {{ $t('admin.system.platformSettings.heading') }}
    <help-button-widget help-key="adminSystemSettingsView" />
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
      <h3>{{ $t('admin.system.platformSettings.headingInfo') }}</h3>

      <!-- PLATFORM TITLE -->
      <n-form-item path="infoPlatformName" :label="$t('models.platformSettings.infoPlatformName')">
        <n-input
          v-model:value="formModel.infoPlatformName"
          type="text"
          :placeholder="$t('models.platformSettings.infoPlatformName')"
          @keydown.enter.prevent
        />
      </n-form-item>
      <!-- PLATFORM DESCRIPTION -->
      <translation-form-item
        v-model="formModel.infoSubtitle"
        parent-form-path-prefix="infoSubtitle"
        :loading="loading"
        :main-form-label="$t('models.platformSettings.infoSubtitle')"
        :translation-form-label="$t('models.platformSettings.infoSubtitle')"
        :translation-form-rule="platformSettingsFormRules.infoSubtitleTranslation"
      />
      <!-- TERMS URL -->
      <n-form-item path="infoTerms" :label="$t('models.platformSettings.infoTerms')">
        <n-input
          v-model:value="formModel.infoTerms"
          type="text"
          :placeholder="$t('models.platformSettings.infoTerms')"
          @keydown.enter.prevent
        />
      </n-form-item>
      <!-- CONTACT NAME -->
      <n-form-item path="infoContactName" :label="$t('models.platformSettings.infoContactName')">
        <n-input
          v-model:value="formModel.infoContactName"
          type="text"
          :placeholder="$t('models.platformSettings.infoContactName')"
          @keydown.enter.prevent
        />
      </n-form-item>
      <!-- CONTACT EMAIL -->
      <n-form-item path="infoContactEmail" :label="$t('models.platformSettings.infoContactEmail')">
        <n-input
          v-model:value="formModel.infoContactEmail"
          type="text"
          :placeholder="$t('models.platformSettings.infoContactEmail')"
          @keydown.enter.prevent
        />
      </n-form-item>
      <!-- CONTACT URL -->
      <n-form-item path="infoContactUrl" :label="$t('models.platformSettings.infoContactUrl')">
        <n-input
          v-model:value="formModel.infoContactUrl"
          type="text"
          :placeholder="$t('models.platformSettings.infoContactUrl')"
          @keydown.enter.prevent
        />
      </n-form-item>

      <n-divider />
      <h3>{{ $t('admin.system.platformSettings.headingOptions') }}</h3>

      <!-- DEFAULT TEXT -->
      <n-form-item path="defaultTextId" :label="$t('models.platformSettings.defaultText')">
        <n-select
          v-model:value="formModel.defaultTextId"
          clearable
          :options="defaultTextOptions"
          :placeholder="$t('admin.system.platformSettings.defaultTextPlaceholder')"
          :consistent-menu-width="false"
          @keydown.enter.prevent
        />
      </n-form-item>

      <!-- AVAILABLE LOCALES -->
      <n-form-item
        path="availableLocales"
        :label="$t('models.platformSettings.availableLocales')"
        required
      >
        <n-select
          v-model:value="formModel.availableLocales"
          multiple
          :options="localeOptions"
          :placeholder="$t('models.platformSettings.availableLocales')"
          :consistent-menu-width="false"
          @keydown.enter.prevent
        />
      </n-form-item>

      <!-- TRANSLATE MAIN NAV INFO ENTRY -->
      <translation-form-item
        v-model="formModel.navInfoEntry"
        parent-form-path-prefix="navInfoEntry"
        :loading="loading"
        :main-form-label="$t('models.platformSettings.navInfoEntry')"
        :translation-form-label="$t('models.platformSettings.navInfoEntry')"
        :translation-form-rule="platformSettingsFormRules.navInfoEntryTranslation"
      />

      <!-- DISPLAY OPTIONS -->
      <n-form-item :label="$t('admin.system.platformSettings.formLabelDisplay')">
        <n-flex vertical>
          <!-- ALWAY SHOW TEXT INFO, ALSO ON NON-TEXT-SPECIFIC PAGES? -->
          <labelled-switch
            v-model="formModel.alwaysShowTextInfo"
            :label="$t('models.platformSettings.alwaysShowTextInfo')"
          />
          <!-- SHOW TEKST FOOTER HINT -->
          <labelled-switch
            v-model="formModel.showTekstFooterHint"
            :label="$t('models.platformSettings.showTekstFooterHint')"
          />
          <!-- SHOW RESOURCE CATEGORY HEADINGS -->
          <labelled-switch
            v-model="formModel.showResourceCategoryHeadings"
            :label="$t('models.platformSettings.showResourceCategoryHeadings')"
          />
          <!-- ALWAYS SHOW RESOURCE CATEGORY HEADINGS -->
          <labelled-switch
            v-model="formModel.alwaysShowResourceCategoryHeadings"
            :label="$t('models.platformSettings.alwaysShowResourceCategoryHeadings')"
          />
          <!-- PRIORITIZE BROWSE LEVEL RESOURCES -->
          <labelled-switch
            v-model="formModel.prioritizeBrowseLevelResources"
            :label="$t('models.platformSettings.prioritizeBrowseLevelResources')"
          />
        </n-flex>
      </n-form-item>

      <n-divider />

      <!-- RESOURCE FONTS -->
      <icon-heading level="3">
        {{ $t('models.platformSettings.customFonts') }}
        <help-button-widget help-key="adminSystemSettingsResourceFonts" />
      </icon-heading>
      <n-form-item v-if="formModel.customFonts" :show-label="false">
        <n-dynamic-input
          v-model:value="formModel.customFonts"
          show-sort-button
          :min="0"
          :max="64"
          @create="() => ''"
        >
          <template #default="{ index }">
            <n-form-item
              ignore-path-change
              :label="$t('models.platformSettings.resourceFontName')"
              :path="`customFonts[${index}]`"
              :rule="platformSettingsFormRules.resourceFontName"
              style="flex-grow: 2"
            >
              <n-input
                v-model:value="formModel.customFonts[index]"
                :placeholder="$t('models.platformSettings.resourceFontName')"
                @keydown.enter.prevent
              />
            </n-form-item>
          </template>
          <template #action="{ index: indexAction, create, remove }">
            <dynamic-input-controls
              top-offset
              :movable="false"
              :insert-disabled="(formModel.customFonts?.length || 0) >= 64"
              @remove="() => remove(indexAction)"
              @insert="() => create(indexAction)"
            />
          </template>
        </n-dynamic-input>
      </n-form-item>

      <n-divider />

      <!-- OSK MODES -->
      <icon-heading level="3">
        {{ $t('models.platformSettings.oskModes') }}
        <help-button-widget help-key="adminSystemSettingsOskModes" />
      </icon-heading>
      <n-form-item v-if="formModel.oskModes" :show-label="false">
        <n-dynamic-input
          v-model:value="formModel.oskModes"
          show-sort-button
          :min="0"
          :max="64"
          @create="() => ({ key: '', name: '', font: '' })"
        >
          <template #default="{ index }">
            <div
              style="
                display: flex;
                align-items: flex-start;
                gap: 12px;
                flex-grow: 2;
                flex-wrap: wrap;
              "
            >
              <n-form-item
                ignore-path-change
                :label="$t('models.platformSettings.oskModeKey')"
                :path="`oskModes[${index}].key`"
                :rule="platformSettingsFormRules.oskModeKey"
                style="flex-grow: 1"
              >
                <n-input
                  v-model:value="formModel.oskModes[index].key"
                  :placeholder="$t('models.platformSettings.oskModeKey')"
                  @keydown.enter.prevent
                />
              </n-form-item>
              <n-form-item
                ignore-path-change
                :label="$t('models.platformSettings.oskModeName')"
                :path="`oskModes[${index}].name`"
                :rule="platformSettingsFormRules.oskModeName"
                style="flex-grow: 2"
              >
                <n-input
                  v-model:value="formModel.oskModes[index].name"
                  :placeholder="$t('models.platformSettings.oskModeName')"
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
                  :placeholder="$t('models.platformSettings.oskModeFont')"
                  :consistent-menu-width="false"
                  style="min-width: 200px"
                  @keydown.enter.prevent
                />
              </n-form-item>
            </div>
          </template>
          <template #action="{ index: indexAction, create, remove, move }">
            <dynamic-input-controls
              top-offset
              :move-up-disabled="indexAction === 0"
              :move-down-disabled="indexAction === formModel.oskModes?.length - 1"
              :insert-disabled="(formModel.customFonts?.length || 0) >= 64"
              @move-up="() => move('up', indexAction)"
              @move-down="() => move('down', indexAction)"
              @remove="() => remove(indexAction)"
              @insert="() => create(indexAction)"
            />
          </template>
        </n-dynamic-input>
      </n-form-item>
    </n-form>
    <button-shelf top-gap>
      <n-button secondary :disabled="!changed" @click="resetForm">{{
        $t('general.resetAction')
      }}</n-button>
      <n-button type="primary" :disabled="!changed" @click="handleSaveClick">{{
        $t('general.saveAction')
      }}</n-button>
    </button-shelf>
  </div>
</template>
