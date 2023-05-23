<script setup lang="ts">
import { ref } from 'vue';
import {
  NForm,
  NInput,
  NColorPicker,
  NCheckbox,
  NFormItem,
  NStep,
  NSteps,
  type FormInst,
  useDialog,
} from 'naive-ui';
import type { TextCreate } from '@/openapi';
import { useFormRules } from '@/formRules';
import StepContainer from '@/components/admin/StepContainer.vue';
import { useStateStore } from '@/stores';
import { onMounted } from 'vue';
import { useI18n } from 'vue-i18n';

const initialModel = (): TextCreate => ({
  title: '',
  subtitle: '',
  slug: '',
  levels: ['book'],
  defaultLevel: 0,
  locDelim: ', ',
  labeledLocation: true,
  accentColor: '#305D97',
});

const state = useStateStore();
const { t } = useI18n({ useScope: 'global' });
const { textFormRules } = useFormRules();
const dialog = useDialog();
const model = ref<TextCreate>(initialModel());
const formRef = ref<FormInst | null>(null);
const currentStep = ref(1);
const currentStatus = ref<'wait' | 'error' | 'finish' | 'process'>('process');

function proceed() {
  currentStep.value++;
}

function finish() {
  console.log('FINISH');
}

onMounted(() => {
  dialog.info({
    title: 'INFO!',
    content: 'INFO!',
    positiveText: t('general.okAction'),
    style: 'font-weight: var(--app-ui-font-weight-light)',
  });
});
</script>

<template>
  <h1>{{ $t('admin.heading') }}: {{ $t('admin.newText.heading') }}</h1>

  <n-steps
    v-if="!state.smallScreen"
    size="small"
    :current="(currentStep as number)"
    :status="currentStatus"
    style="margin: 2rem 0"
  >
    <n-step title="I Me Mine" description="All through the day, I me mine I me mine, I me mine" />
    <n-step
      title="Let It Be"
      description="When I find myself in times of trouble Mother Mary comes to me"
    />
    <n-step title="Come Together" description="Here come old flat top He come grooving up slowly" />
  </n-steps>

  <div class="content-block">
    <n-form
      ref="formRef"
      :model="model"
      :rules="textFormRules"
      label-placement="top"
      label-width="auto"
      require-mark-placement="right-hanging"
    >
      <StepContainer
        :step-no="1"
        :current-step="currentStep"
        :submit-button-label="$t('admin.newText.btnProceed')"
        @submit="proceed"
      >
        <n-form-item path="title" :label="$t('models.text.title')">
          <n-input
            v-model:value="model.title"
            type="text"
            :placeholder="$t('models.text.title')"
            @keydown.enter.prevent
            :disabled="false"
          />
        </n-form-item>
        <n-form-item path="subtitle" :label="$t('models.text.subtitle')">
          <n-input
            v-model:value="model.subtitle"
            type="text"
            :placeholder="$t('models.text.subtitle')"
            @keydown.enter.prevent
            :disabled="false"
          />
        </n-form-item>
        <n-form-item path="slug" :label="$t('models.text.slug')">
          <n-input
            v-model:value="model.slug"
            type="text"
            :placeholder="$t('models.text.slug')"
            @keydown.enter.prevent
            :disabled="false"
          />
        </n-form-item>
      </StepContainer>

      <StepContainer
        :step-no="2"
        :current-step="currentStep"
        :submit-button-label="$t('admin.newText.btnProceed')"
        @submit="proceed"
      >
        - LEVELS<br />
        - DEFAULT LEVEL
      </StepContainer>

      <StepContainer
        :step-no="3"
        :current-step="currentStep"
        :submit-button-label="$t('admin.newText.btnFinish')"
        @submit="finish"
      >
        <n-form-item path="locDelim" :label="$t('models.text.locDelim')">
          <n-input
            v-model:value="model.locDelim"
            type="text"
            :placeholder="$t('models.text.locDelim')"
            @keydown.enter.prevent
            :disabled="false"
          />
        </n-form-item>
        <n-form-item path="labeledLocation" :label="$t('models.text.labeledLocation')">
          <n-checkbox v-model:checked="model.labeledLocation" :disabled="false">
            {{ $t('models.text.labeledLocation') }}
          </n-checkbox>
        </n-form-item>
        <n-form-item path="accentColor" :label="$t('models.text.accentColor')">
          <n-color-picker
            v-model:value="model.accentColor"
            :modes="['hex']"
            :show-alpha="false"
            :swatches="[
              '#305D97',
              '#097F86',
              '#43895F',
              '#D49101',
              '#D26E2B',
              '#D43A35',
              '#B83E63',
              '#88447F',
            ]"
          />
        </n-form-item>
      </StepContainer>
    </n-form>
  </div>
</template>

<style scoped></style>
