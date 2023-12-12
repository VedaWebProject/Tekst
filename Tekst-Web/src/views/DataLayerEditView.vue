<script setup lang="ts">
import { type AnyLayerUpdate, PATCH, type UserReadPublic } from '@/api';
import { $t } from '@/i18n';
import { useAuthStore, useStateStore } from '@/stores';
import HelpButtonWidget from '@/components/widgets/HelpButtonWidget.vue';
import IconHeading from '@/components/typography/IconHeading.vue';
import { useMessages } from '@/messages';
import { computed, ref, watch, type VNodeChild, h } from 'vue';
import _cloneDeep from 'lodash.clonedeep';
import { RouterLink } from 'vue-router';
import {
  NCollapse,
  NCollapseItem,
  NSelect,
  NSpace,
  NIcon,
  NDynamicInput,
  NSpin,
  NForm,
  NFormItem,
  NInput,
  NButton,
  NTag,
  type FormInst,
  type SelectOption,
} from 'naive-ui';
import { layerFormRules } from '@/forms/formRules';
import { useModelChanges } from '@/modelChanges';
import UserDisplay from '@/components/UserDisplay.vue';
import { useRoute } from 'vue-router';
import { useUsersPublic } from '@/fetchers';
import { useRouter } from 'vue-router';
import ButtonFooter from '@/components/ButtonFooter.vue';

import LayersFilled from '@vicons/material/LayersFilled';
import MinusRound from '@vicons/material/MinusRound';
import AddRound from '@vicons/material/AddRound';
import KeyboardArrowLeftOutlined from '@vicons/material/KeyboardArrowLeftOutlined';
import PersonFilled from '@vicons/material/PersonFilled';
import TranslationFormItem from '@/forms/TranslationFormItem.vue';
import { usePlatformData } from '@/platformData';
import { pickTranslation } from '@/utils';
import { useLayersStore } from '@/stores/layers';

const { message } = useMessages();
const route = useRoute();
const router = useRouter();
const state = useStateStore();
const auth = useAuthStore();
const { pfData } = usePlatformData();

const layers = useLayersStore();
const { users, loading: loadingUsers, error: errorUsers } = useUsersPublic();
const layer = layers.data.find((l) => l.id === route.params.id);
const getInitialModel = () => _cloneDeep(layer);

const formRef = ref<FormInst | null>(null);
const loadingSave = ref(false);
const loading = computed(() => layers.loading || loadingUsers.value || loadingSave.value);
const model = ref<AnyLayerUpdate | undefined>(getInitialModel());
const { changed, reset, getChanges } = useModelChanges(model);

const categoryOptions = computed(
  () =>
    pfData.value?.settings.layerCategories?.map((c) => ({
      label: pickTranslation(c.translations, state.locale) || c.key,
      value: c.key,
    })) || []
);

const shareWriteOptions = computed(() =>
  model.value
    ? (users.value || []).map((u) => {
        return {
          value: u.id,
          disabled: u.id === auth.user?.id || !!model.value?.sharedRead?.find((s) => s === u.id),
          user: u,
        };
      })
    : []
);

const shareReadOptions = computed(() =>
  model.value
    ? (users.value || []).map((u) => {
        return {
          value: u.id,
          disabled: u.id === auth.user?.id || !!model.value?.sharedWrite?.find((s) => s === u.id),
          user: u,
        };
      })
    : []
);

// change route if text changes
watch(
  () => state.text,
  (newText) => {
    router.push({ name: 'dataLayers', params: { text: newText?.slug } });
  }
);

function handleResetClick() {
  model.value = getInitialModel();
  reset();
}

async function handleSaveClick() {
  loadingSave.value = true;
  formRef.value
    ?.validate(async (validationError) => {
      if (validationError || !model.value) return;
      const { data, error } = await PATCH('/layers/{id}', {
        params: { path: { id: layer?.id || '' } },
        body: {
          ...(getChanges() as AnyLayerUpdate),
          layerType: model.value.layerType,
        },
      });
      if (!error) {
        message.success($t('dataLayers.edit.msgSaved', { title: data.title }));
        layers.replace(data);
      } else {
        message.error($t('errors.unexpected'), error);
      }
      loadingSave.value = false;
    })
    .catch(() => {
      message.error($t('errors.followFormRules'));
      loadingSave.value = false;
    });
}

function renderUserSelectLabel(option: SelectOption): VNodeChild {
  return h(UserDisplay, { user: option.user as UserReadPublic });
}

function renderUserSelectTag(props: { option: SelectOption; handleClose: () => void }): VNodeChild {
  return h(
    NTag,
    {
      closable: true,
      bordered: false,
      onMousedown: (e: FocusEvent) => {
        e.preventDefault();
      },
      onClose: (e: MouseEvent) => {
        e.stopPropagation();
        props.handleClose();
      },
    },
    {
      default: () => `@${(props.option.user as UserReadPublic).username}`,
      icon: () => h(NIcon, null, { default: () => h(PersonFilled) }),
    }
  );
}
</script>

<template>
  <IconHeading v-if="layer" level="1" :icon="LayersFilled">
    {{ $t('dataLayers.edit.heading') }}
    <HelpButtonWidget help-key="dataLayerEditView" />
  </IconHeading>

  <router-link
    v-slot="{ navigate }"
    :to="{ name: 'dataLayers', params: { text: state.text?.slug } }"
    custom
  >
    <n-button text :focusable="false" @click="navigate">
      <template #icon>
        <KeyboardArrowLeftOutlined />
      </template>
      {{ $t('dataLayers.edit.backToOverview') }}
    </n-button>
  </router-link>

  <div v-if="model" class="content-block">
    <h2>{{ layer?.title }}</h2>

    <table>
      <tbody>
        <tr v-if="users && model.ownerId">
          <td>{{ $t('models.user.modelLabel') }}:</td>
          <td>{{ layer?.owner?.username }}</td>
        </tr>
      </tbody>
    </table>

    <n-form
      ref="formRef"
      :model="model"
      :rules="layerFormRules"
      label-placement="top"
      label-width="auto"
      require-mark-placement="right-hanging"
    >
      <n-collapse>
        <!-- TITLE -->
        <n-form-item path="title" :label="$t('models.layer.title')" required>
          <n-input
            v-model:value="model.title"
            type="text"
            :placeholder="$t('models.layer.title')"
            :disabled="loading"
            @keydown.enter.prevent
          />
        </n-form-item>
        <!-- DESCRIPTION -->
        <TranslationFormItem
          v-model:value="model.description"
          parent-form-path-prefix="description"
          :loading="loading"
          :disabled="loading"
          :main-form-label="$t('models.layer.description')"
          :translation-form-label="$t('models.layer.description')"
          :translation-form-rule="layerFormRules.descriptionTranslation"
        />
        <!-- CATEGORY -->
        <n-form-item :label="$t('models.layer.category')">
          <n-select
            v-model:value="model.category"
            clearable
            :loading="loading"
            :placeholder="$t('browse.uncategorized')"
            :options="categoryOptions"
          />
        </n-form-item>
        <!-- CITATION -->
        <n-form-item path="citation" :label="$t('models.layer.citation')">
          <n-input
            v-model:value="model.citation"
            type="text"
            :placeholder="$t('models.layer.citation')"
            :disabled="loading"
            @keydown.enter.prevent
          />
        </n-form-item>
        <!-- COMMENT -->
        <TranslationFormItem
          v-model:value="model.comment"
          parent-form-path-prefix="comment"
          multiline
          :max-translation-length="2000"
          :loading="loading"
          :disabled="loading"
          :main-form-label="$t('models.layer.comment')"
          :translation-form-label="$t('models.layer.comment')"
          :translation-form-rule="layerFormRules.commentTranslation"
        />
        <!-- METADATA -->
        <n-collapse-item :title="$t('models.meta.modelLabel')" name="meta">
          <n-form-item
            v-if="model.meta"
            :label="$t('models.meta.modelLabel')"
            :show-feedback="false"
          >
            <n-dynamic-input
              v-model:value="model.meta"
              item-style="margin-bottom: 0;"
              :min="0"
              :max="64"
              @create="() => ({ key: '', value: '' })"
            >
              <template #default="{ index }">
                <div style="display: flex; align-items: flex-start; gap: 12px; width: 100%">
                  <n-form-item
                    ignore-path-change
                    :show-label="false"
                    :path="`meta[${index}].key`"
                    :rule="layerFormRules.metaKey"
                    required
                  >
                    <n-input
                      v-model:value="model.meta[index].key"
                      :placeholder="$t('models.meta.key')"
                      @keydown.enter.prevent
                    />
                  </n-form-item>
                  <n-form-item
                    ignore-path-changechange
                    :show-label="false"
                    :path="`meta[${index}].value`"
                    :rule="layerFormRules.metaValue"
                    style="flex-grow: 2"
                    required
                  >
                    <n-input
                      v-model:value="model.meta[index].value"
                      :placeholder="$t('models.meta.value')"
                      @keydown.enter.prevent
                    />
                  </n-form-item>
                </div>
              </template>
              <template #action="{ index: indexAction, create, remove }">
                <n-space style="margin-left: 20px; flex-wrap: nowrap">
                  <n-button
                    secondary
                    circle
                    :title="$t('general.removeAction')"
                    @click="() => remove(indexAction)"
                  >
                    <template #icon>
                      <n-icon :component="MinusRound" />
                    </template>
                  </n-button>
                  <n-button
                    secondary
                    circle
                    :title="$t('general.insertAction')"
                    :disabled="model.meta.length >= 64"
                    @click="() => create(indexAction)"
                  >
                    <template #icon>
                      <n-icon :component="AddRound" />
                    </template>
                  </n-button>
                </n-space>
              </template>
            </n-dynamic-input>
          </n-form-item>
        </n-collapse-item>
        <!-- SHARES -->
        <n-collapse-item
          v-if="auth.user?.isSuperuser || auth.user?.id === layer?.owner?.id"
          :disabled="!layer || layer.public"
          :title="
            $t('models.layer.share') +
            (!layer || layer.public ? ` ${$t('dataLayers.edit.onlyForUnpublished')}` : '')
          "
          name="shares"
        >
          <n-form-item path="sharedRead" :label="$t('models.layer.sharedRead')">
            <n-select
              v-model:value="model.sharedRead"
              multiple
              filterable
              :render-label="renderUserSelectLabel"
              :render-tag="renderUserSelectTag"
              :loading="loadingUsers"
              :status="errorUsers ? 'error' : undefined"
              :placeholder="$t('models.layer.sharedRead')"
              :options="shareReadOptions"
            />
          </n-form-item>
          <n-form-item path="sharedWrite" :label="$t('models.layer.sharedWrite')">
            <n-select
              v-model:value="model.sharedWrite"
              multiple
              filterable
              :render-label="renderUserSelectLabel"
              :render-tag="renderUserSelectTag"
              :loading="loadingUsers"
              :status="errorUsers ? 'error' : undefined"
              :placeholder="$t('models.layer.sharedWrite')"
              :options="shareWriteOptions"
            />
          </n-form-item>
        </n-collapse-item>
      </n-collapse>
    </n-form>

    <ButtonFooter>
      <n-button secondary :disabled="!changed" @click="handleResetClick">{{
        $t('general.resetAction')
      }}</n-button>
      <n-button type="primary" :disabled="!changed" @click="handleSaveClick">{{
        $t('general.saveAction')
      }}</n-button>
    </ButtonFooter>
  </div>

  <n-spin v-else-if="loading" size="large" style="width: 100%" />
</template>
