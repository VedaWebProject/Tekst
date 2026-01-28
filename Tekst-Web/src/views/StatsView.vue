<script setup lang="ts">
import { GET, type SuperuserStats, type UserStats } from '@/api';
import IconHeading from '@/components/generic/IconHeading.vue';
import { useMessages } from '@/composables/messages';
import { $t, getLocaleProfile } from '@/i18n';
import { ErrorIcon, StatsIcon } from '@/icons';
import { useAuthStore, useStateStore } from '@/stores';
import { NEmpty, NFlex, NIcon, NSpin, NStatistic } from 'naive-ui';
import { computed, onMounted, ref } from 'vue';

const state = useStateStore();
const auth = useAuthStore();
const { message } = useMessages();
const stats = ref<UserStats | SuperuserStats | undefined>();
const loading = ref(true);

const localeCode = computed(() => getLocaleProfile(state.locale).displayShort);

async function loadStats() {
  loading.value = true;
  const { data, error } = await GET('/platform/stats');
  if (!error) {
    stats.value = data;
  } else {
    message.error($t('errors.unexpected'));
  }
  loading.value = false;
}

onMounted(() => {
  loadStats();
});
</script>

<template>
  <icon-heading :icon="StatsIcon" level="1">
    {{ $t('stats.heading') }}
  </icon-heading>

  <n-spin v-if="loading" class="centered-spin" />

  <n-empty v-else-if="!stats" :description="$t('errors.unexpected')">
    <template #icon>
      <n-icon :component="ErrorIcon" />
    </template>
  </n-empty>

  <template v-else>
    <div class="content-block">
      <!-- GENERAL NUMBERS -->
      <h2>{{ $t('common.general') }}</h2>
      <n-flex :size="[32, 24]">
        <n-statistic
          :label="$t('common.text', 2)"
          :value="stats.texts.toLocaleString(localeCode)"
        />
        <n-statistic
          :label="$t('common.location', 2)"
          :value="stats.locations.toLocaleString(localeCode)"
        />
        <n-statistic
          :label="$t('models.resource.modelLabel', 2)"
          :value="stats.resources.toLocaleString(localeCode)"
        />
        <n-statistic
          :label="$t('common.content', 2)"
          :value="stats.contents.toLocaleString(localeCode)"
        />
        <n-statistic
          :label="$t('admin.users.heading')"
          :value="stats.users.toLocaleString(localeCode)"
        />
        <n-statistic
          v-if="auth.user?.isSuperuser"
          :label="$t('stats.general.msgSent')"
          :value="(stats as SuperuserStats).messages.toLocaleString(localeCode)"
          class="su-stat"
          :title="$t('stats.onlySu')"
        />
        <n-statistic
          v-if="auth.user?.isSuperuser"
          :label="$t('stats.general.emailsSent')"
          :value="(stats as SuperuserStats).emails.toLocaleString(localeCode)"
          class="su-stat"
          :title="$t('stats.onlySu')"
        />
      </n-flex>
    </div>
    <div class="content-block">
      <!-- USER ACTIVITY -->
      <h2>{{ $t('stats.activity.heading') }}</h2>
      <n-flex :size="[32, 24]">
        <n-statistic
          v-if="auth.user?.isSuperuser"
          :label="$t('stats.activity.active')"
          class="su-stat"
          :title="$t('stats.onlySu')"
          :value="(stats as SuperuserStats).activeSessions.toLocaleString(localeCode)"
        />
        <n-statistic
          :label="$t('stats.activity.pastWeek')"
          :value="stats.activeUsersCountPastWeek.toLocaleString(localeCode)"
        >
          <template #suffix>
            <span class="text-medium ml-sm">
              {{ ((stats.activeUsersCountPastWeek / stats.users) * 100).toFixed(2) }}%
            </span>
          </template>
        </n-statistic>
        <n-statistic
          :label="$t('stats.activity.pastMonth')"
          :value="stats.activeUsersCountPastMonth.toLocaleString(localeCode)"
        >
          <template #suffix>
            <span class="text-medium ml-sm">
              {{ ((stats.activeUsersCountPastMonth / stats.users) * 100).toFixed(2) }}%
            </span>
          </template>
        </n-statistic>
        <n-statistic
          :label="$t('stats.activity.pastYear')"
          :value="stats.activeUsersCountPastYear.toLocaleString(localeCode)"
        >
          <template #suffix>
            <span class="text-medium ml-sm">
              {{ ((stats.activeUsersCountPastYear / stats.users) * 100).toFixed(2) }}%
            </span>
          </template>
        </n-statistic>
        <n-statistic
          v-if="auth.user?.isSuperuser"
          :label="$t('stats.activity.logins')"
          class="su-stat"
          :title="$t('stats.onlySu')"
          :value="(stats as SuperuserStats).logins.toLocaleString(localeCode)"
        />
        <n-statistic
          v-if="auth.user?.isSuperuser"
          :label="$t('contents.corrections.notes')"
          :value="(stats as SuperuserStats).corrections.toLocaleString(localeCode)"
          class="su-stat"
          :title="$t('stats.onlySu')"
        />
        <n-statistic
          v-if="auth.user?.isSuperuser"
          :label="$t('browse.bookmarks.bookmarks')"
          :value="(stats as SuperuserStats).bookmarks.toLocaleString(localeCode)"
          class="su-stat"
          :title="$t('stats.onlySu')"
        />
        <n-statistic
          v-if="auth.user?.isSuperuser"
          :label="$t('stats.general.msgSent')"
          :value="(stats as SuperuserStats).messagesUser.toLocaleString(localeCode)"
          class="su-stat"
          :title="$t('stats.onlySu')"
        />
        <n-statistic
          :label="$t('stats.search.quick')"
          :value="stats.searchQuick.toLocaleString(localeCode)"
        />
        <n-statistic
          :label="$t('stats.search.advanced')"
          :value="stats.searchAdvanced.toLocaleString(localeCode)"
        />
        <n-statistic
          :label="$t('stats.activity.statsRequests')"
          :value="stats.statsRequests.toLocaleString(localeCode)"
        />
        <n-statistic
          v-if="auth.user?.isSuperuser"
          :label="$t('stats.activity.changedPws')"
          :value="(stats as SuperuserStats).changedPasswords.toLocaleString(localeCode)"
          class="su-stat"
          :title="$t('stats.onlySu')"
        />
        <n-statistic
          v-if="auth.user?.isSuperuser"
          :label="$t('stats.activity.forgottenPws')"
          :value="(stats as SuperuserStats).forgottenPasswords.toLocaleString(localeCode)"
          class="su-stat"
          :title="$t('stats.onlySu')"
        />
        <n-statistic
          v-if="auth.user?.isSuperuser"
          :label="$t('stats.activity.resetPws')"
          :value="(stats as SuperuserStats).resetPasswords.toLocaleString(localeCode)"
          class="su-stat"
          :title="$t('stats.onlySu')"
        />
        <n-statistic
          v-if="auth.user?.isSuperuser"
          :label="$t('stats.activity.deletedUsers')"
          :value="(stats as SuperuserStats).deletedUsers.toLocaleString(localeCode)"
          class="su-stat"
          :title="$t('stats.onlySu')"
        />
      </n-flex>
    </div>
  </template>
</template>

<style scoped>
.su-stat :deep(.n-statistic__label) {
  color: var(--info-color);
}
</style>
