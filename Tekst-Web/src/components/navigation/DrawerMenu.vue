<script setup lang="ts">
import { NDrawer, NDrawerContent } from 'naive-ui';
import { computed } from 'vue';
import NavigationMenu from '@/components/navigation/NavigationMenu.vue';
import ThemeModeSwitcher from '@/components/widgets/ThemeModeSwitcher.vue';
import LocaleSwitcher from '@/components/widgets/LocaleSwitcher.vue';
import UserOptionsButton from '@/components/widgets/UserOptionsButton.vue';
import QuickSearchWidget from '@/components/widgets/QuickSearch.vue';
import HelpNavButton from '@/components/widgets/HelpNavButton.vue';
import {
  useAccountMenuOptions,
  useAdminMenuOptions,
  useMainMenuOptions,
} from '@/components/navigation/navMenuOptions';
import { $t } from '@/i18n';
import { useAuthStore } from '@/stores';

withDefaults(
  defineProps<{
    show?: boolean;
    showUserOptionsButton?: boolean;
  }>(),
  {
    show: false,
    showUserOptionsButton: false,
  }
);

defineEmits(['update:show']);

const auth = useAuthStore();
const { menuOptions: mainMenuOptions } = useMainMenuOptions();
const { menuOptions: accountMenuOptions } = useAccountMenuOptions();
const { menuOptions: adminMenuOptions } = useAdminMenuOptions();

const allMenuOptions = computed(() => [
  {
    type: 'group',
    key: 'general-group',
    label: $t('general.platform'),
    children: mainMenuOptions.value
      .concat(mainMenuOptions.value.find((o) => o.key === 'info')?.children || [])
      .filter((o) => o.key !== 'info'),
  },
  {
    type: 'group',
    key: 'account-group',
    label: `${auth.user?.firstName} ${auth.user?.lastName}`,
    children: accountMenuOptions,
  },
  {
    type: 'group',
    key: 'admin-group',
    label: $t('admin.heading'),
    children: adminMenuOptions.value,
  },
]);
</script>

<template>
  <n-drawer
    :show="show"
    :width="600"
    :auto-focus="false"
    to="#app-container"
    style="max-width: 90%"
    @update:show="$emit('update:show', $event)"
  >
    <n-drawer-content closable header-style="background-color: var(--accent-color-fade5);">
      <template #header>
        <div class="header-buttons">
          <QuickSearchWidget />
          <ThemeModeSwitcher />
          <LocaleSwitcher />
          <HelpNavButton />
          <UserOptionsButton v-if="showUserOptionsButton" />
        </div>
      </template>
      <NavigationMenu mode="vertical" :options="allMenuOptions" />
    </n-drawer-content>
  </n-drawer>
</template>

<style scoped>
.header-buttons {
  display: flex;
  align-items: center;
  justify-content: space-around;
  gap: 4px;
  width: 60%;
  max-width: 80vw;
  margin: 0 auto;
}
</style>
