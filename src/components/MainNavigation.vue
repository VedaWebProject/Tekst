<script setup lang="ts">
import { h, ref, computed, watch, type Component } from 'vue';
import { useRoute, RouterLink } from 'vue-router';
import { useWindowSize } from '@vueuse/core';
import { NIcon, NMenu } from 'naive-ui';
import type { MenuOption } from 'naive-ui';
import BookFilled from '@vicons/material/BookFilled';
import PersonFilled from '@vicons/material/PersonFilled';
import WineBarFilled from '@vicons/material/WineBarFilled';

const route = useRoute();
const activeRouteName = computed(() => route.name?.toString() || null);
const activeKey = ref<string | null>(activeRouteName.value);
watch(activeRouteName, (newRouteName) => (activeKey.value = newRouteName));

const { width } = useWindowSize();

function renderIcon(icon: Component) {
  return () => h(NIcon, null, { default: () => h(icon) });
}

function renderRouterLink(name: string, label: string, params?: Record<string, string>) {
  return () =>
    h(
      RouterLink,
      {
        to: {
          name: name,
          params: params,
        },
      },
      { default: () => label }
    );
}

const menuOptions: MenuOption[] = [
  {
    label: renderRouterLink('home', 'Home'),
    key: 'home',
    icon: renderIcon(BookFilled),
  },
  {
    label: renderRouterLink('about', 'About'),
    key: 'about',
    icon: renderIcon(BookFilled),
  },
  {
    label: renderRouterLink('account', 'Account'),
    key: 'account',
    icon: renderIcon(BookFilled),
  },
  {
    label: renderRouterLink('admin', 'Admin'),
    key: 'admin',
    icon: renderIcon(BookFilled),
  },
  {
    label: 'Test 1',
    key: 'test-1',
    disabled: true,
    icon: renderIcon(BookFilled),
  },
  {
    label: 'Test 2',
    key: 'test-2',
    icon: renderIcon(BookFilled),
    children: [
      {
        type: 'group',
        label: 'People',
        key: 'people',
        children: [
          {
            label: 'Narrator',
            key: 'narrator',
            icon: renderIcon(PersonFilled),
          },
          {
            label: 'Sheep Man',
            key: 'sheep-man',
            icon: renderIcon(PersonFilled),
          },
        ],
      },
      {
        label: 'Beverage',
        key: 'beverage',
        icon: renderIcon(WineBarFilled),
        children: [
          {
            label: 'Whisky',
            key: 'whisky',
          },
        ],
      },
      {
        label: 'Food',
        key: 'food',
        children: [
          {
            label: 'Sandwich',
            key: 'sandwich',
          },
        ],
      },
      {
        label: 'The past increases. The future recedes.',
        key: 'the-past-increases-the-future-recedes',
      },
    ],
  },
];
</script>

<template>
  <n-menu
    :value="activeKey"
    :mode="width > 600 ? 'horizontal' : 'vertical'"
    :options="menuOptions"
    @update:value="
      (k) => {
        activeKey = k;
      }
    "
  />
</template>

<style scoped></style>
