<script setup lang="ts">
import { type AnyLayerRead, type AnyLayerUpdate, PATCH } from '@/api';
import { $t } from '@/i18n';
import { useAuthStore, useBrowseStore, useStateStore } from '@/stores';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
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
  type FormInst,
  type SelectOption,
} from 'naive-ui';
import { layerFormRules } from '@/formRules';
import { useModelChanges } from '@/modelChanges';
import UserDisplay from '@/components/UserDisplay.vue';
import { useRoute } from 'vue-router';
import { useLayers, useUsersPublic } from '@/fetchers';
import { useRouter } from 'vue-router';
import ButtonFooter from '@/components/ButtonFooter.vue';

import LayersFilled from '@vicons/material/LayersFilled';
import MinusRound from '@vicons/material/MinusRound';
import AddRound from '@vicons/material/AddRound';
import KeyboardArrowLeftOutlined from '@vicons/material/KeyboardArrowLeftOutlined';

const { message } = useMessages();
const route = useRoute();
const router = useRouter();
const state = useStateStore();
const browse = useBrowseStore();
const auth = useAuthStore();

const textId = computed(() => state.text?.id || '');
const { layers, loading: loadingLayers } = useLayers(textId);
const { users, loading: loadingUsers, error: errorUsers } = useUsersPublic();

const layer = computed<AnyLayerRead | undefined>(() =>
  layers.value.find((l) => l.id === route.params.id)
);

const getInitialModel = () => _cloneDeep(layer.value);

const formRef = ref<FormInst | null>(null);
const loadingSave = ref(false);
const loading = computed(() => loadingLayers.value || loadingUsers.value || loadingSave.value);
const model = ref<AnyLayerUpdate | undefined>(getInitialModel());
const { changed, reset, getChanges } = useModelChanges(model);

const shareOptions = computed(() =>
  (users.value || [])
    .filter((u) => u.id !== auth.user?.id)
    .map((u) => {
      return { value: u.id, user: u };
    })
);

// set initial model as soon as layers are loaded
watch(layer, () => {
  model.value = getInitialModel();
  reset();
});

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
        params: { path: { id: layer.value?.id || '' } },
        body: {
          ...(getChanges() as AnyLayerUpdate),
          layerType: model.value.layerType,
        },
      });
      if (!error) {
        message.success($t('YAY'));
        layers.value = layers.value.map((l) => (l.id === data.id ? data : l));
        await browse.loadLayersData();
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
  return h(UserDisplay, { user: option.user });
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
        <n-form-item path="description" :label="$t('models.layer.description')">
          <n-input
            v-model:value="model.description"
            type="text"
            :placeholder="$t('models.layer.description')"
            :disabled="loading"
            @keydown.enter.prevent
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
        <n-form-item path="comment" :label="$t('models.layer.comment')">
          <n-input
            v-model:value="model.comment"
            type="textarea"
            :placeholder="$t('models.layer.comment')"
            :disabled="loading"
          />
        </n-form-item>
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
              :loading="loadingUsers"
              :status="errorUsers ? 'error' : undefined"
              :placeholder="$t('models.layer.sharedRead')"
              :options="shareOptions"
            />
          </n-form-item>
          <n-form-item path="sharedWrite" :label="$t('models.layer.sharedWrite')">
            <n-select
              v-model:value="model.sharedWrite"
              multiple
              filterable
              :render-label="renderUserSelectLabel"
              :loading="loadingUsers"
              :status="errorUsers ? 'error' : undefined"
              :placeholder="$t('models.layer.sharedWrite')"
              :options="shareOptions"
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
