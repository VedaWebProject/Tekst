<script setup lang="ts">
import type { PublicUserSearchFilters } from '@/api';
import IconHeading from '@/components/generic/IconHeading.vue';
import HelpButtonWidget from '@/components/HelpButtonWidget.vue';
import UserAvatar from '@/components/user/UserAvatar.vue';
import UserThingHeader from '@/components/user/UserThingHeader.vue';
import { usePublicUserSearch } from '@/composables/publicUserSearch';
import { $t } from '@/i18n';
import { CommunityIcon, ErrorIcon, NoContentIcon, SearchIcon } from '@/icons';
import { useStateStore } from '@/stores';
import { createReusableTemplate } from '@vueuse/core';
import { NEmpty, NFlex, NIcon, NInput, NList, NListItem, NPagination, NSpin } from 'naive-ui';
import { computed, ref } from 'vue';
import { RouterLink } from 'vue-router';

const state = useStateStore();
const [DefineTemplate, ReuseTemplate] = createReusableTemplate();

const defaultPage = 1;
const paginationSlots = computed(() => (state.smallScreen ? 4 : 9));

const initialFilters = (): PublicUserSearchFilters => ({
  q: '',
  pg: defaultPage,
  pgs: 10,
  emptyOk: true,
});

const filters = ref<PublicUserSearchFilters>(initialFilters());
const { users, total, error, loading } = usePublicUserSearch(filters);

function resetPagination() {
  filters.value.pg = defaultPage;
}
</script>

<template>
  <icon-heading level="1" :icon="CommunityIcon">
    {{ $t('common.community') }}
    <help-button-widget help-key="communityView" />
  </icon-heading>

  <define-template>
    <!-- Pagination -->
    <n-flex v-if="!!total" justify="end" class="pagination-container">
      <n-pagination
        v-model:page="filters.pg"
        v-model:page-size="filters.pgs"
        :simple="state.smallScreen"
        :default-page-size="10"
        :page-slot="paginationSlots"
        :disabled="loading"
        :item-count="total"
        :page-sizes="[10, 25, 50]"
        size="medium"
        show-size-picker
      />
    </n-flex>
  </define-template>

  <n-input
    v-model:value="filters.q"
    round
    clearable
    :placeholder="$t('common.searchAction')"
    class="mb-md"
    @update:value="resetPagination"
  >
    <template #prefix>
      <n-icon :component="SearchIcon" />
    </template>
  </n-input>

  <n-spin v-if="loading" class="centered-spinner" :description="$t('common.loading')" />

  <n-empty v-else-if="error" :description="$t('errors.unexpected')">
    <template #icon>
      <n-icon :component="ErrorIcon" />
    </template>
  </n-empty>

  <template v-else-if="total">
    <div class="text-small translucent">
      {{ $t('admin.users.msgFoundCount', { count: total }) }}
    </div>

    <!-- Users List -->
    <div class="content-block">
      <template v-if="!!total">
        <!-- Pagination -->
        <reuse-template />
        <n-list style="background-color: transparent; margin: var(--gap-lg) 0" hoverable clickable>
          <router-link
            v-for="user in users"
            :key="user.id"
            v-slot="{ navigate }"
            :to="{ name: 'user', params: { username: user.username } }"
            custom
          >
            <n-list-item @click="navigate">
              <n-flex :wrap="false">
                <user-avatar :username="user.username" :avatar-url="user.avatarUrl" :size="64" />
                <user-thing-header :user="user" />
              </n-flex>
            </n-list-item>
          </router-link>
        </n-list>
        <!-- Pagination -->
        <reuse-template />
      </template>
      <template v-else>
        {{ $t('search.nothingFound') }}
      </template>
    </div>
  </template>

  <n-empty v-else :description="$t('admin.users.msgFoundCount', { count: total })">
    <template #icon>
      <n-icon :component="NoContentIcon" />
    </template>
  </n-empty>
</template>

<style scoped>
.pagination-container:first-child {
  margin-bottom: var(--gap-lg);
}

.pagination-container:last-child {
  margin-top: var(--gap-lg);
}
</style>
