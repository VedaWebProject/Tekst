<script setup lang="ts">
import type { UserRead } from '@/api';
import {
  NIcon,
  NTime,
  NBadge,
  NListItem,
  NThing,
  NFlex,
  NButton,
  NDropdown,
  type DropdownOption,
} from 'naive-ui';
import { usePlatformData } from '@/composables/platformData';
import { computed } from 'vue';
import { $t } from '@/i18n';
import UserAvatar from '@/components/user/UserAvatar.vue';
import { RouterLink } from 'vue-router';
import {
  VerifiedUserIcon,
  MoreIcon,
  DeleteIcon,
  CheckCircleIcon,
  BlockCircleIcon,
  UserPromoteIcon,
  UserDowngradeIcon,
  StarIcon,
} from '@/icons';
import { renderIcon, utcToLocalTime } from '@/utils';

const props = defineProps<{
  targetUser: UserRead;
  currentUser?: UserRead;
}>();

const emit = defineEmits([
  'setSuperuserClick',
  'unsetSuperuserClick',
  'activateClick',
  'verifyClick',
  'deleteClick',
]);

const { pfData } = usePlatformData();

const targetUserIsCurrentUser = computed(() => props.targetUser.id === props.currentUser?.id);
const emailLink = computed(
  () =>
    `mailto:${props.targetUser.email}?subject=${$t('admin.users.mailtoSubject', {
      platform: pfData.value?.state.platformName,
    })}`
);

const actionOptions = computed(() => [
  {
    type: 'group',
    label: $t('admin.users.userItemActions.lblGroupAccountStatus'),
    children: [
      ...(props.targetUser.isActive
        ? [
            {
              label: $t('admin.users.userItemActions.setInactive'),
              key: 'setInactive',
              icon: renderIcon(BlockCircleIcon, 'var(--col-error)'),
              disabled: targetUserIsCurrentUser.value,
              action: () => emit('activateClick', props.targetUser, false),
            },
          ]
        : [
            {
              label: $t('admin.users.userItemActions.setActive'),
              key: 'setActive',
              icon: renderIcon(CheckCircleIcon, 'var(--col-success'),
              disabled: targetUserIsCurrentUser.value,
              action: () => emit('activateClick', props.targetUser, true),
            },
          ]),
      ...(props.targetUser.isVerified
        ? [
            {
              label: $t('admin.users.userItemActions.setUnverified'),
              key: 'setUnverified',
              icon: renderIcon(VerifiedUserIcon, 'var(--col-error'),
              disabled: targetUserIsCurrentUser.value,
              action: () => emit('verifyClick', props.targetUser, false),
            },
          ]
        : [
            {
              label: $t('admin.users.userItemActions.setVerified'),
              key: 'setVerified',
              icon: renderIcon(VerifiedUserIcon, 'var(--col-success'),
              disabled: targetUserIsCurrentUser.value,
              action: () => emit('verifyClick', props.targetUser, true),
            },
          ]),
      ...(props.targetUser.isSuperuser
        ? [
            {
              label: $t('admin.users.userItemActions.unsetSuperuser'),
              key: 'setUser',
              icon: renderIcon(UserDowngradeIcon, 'var(--col-error'),
              disabled: targetUserIsCurrentUser.value,
              action: () => emit('setSuperuserClick', props.targetUser, false),
            },
          ]
        : [
            {
              label: $t('admin.users.userItemActions.setSuperuser'),
              key: 'setSuperuser',
              icon: renderIcon(UserPromoteIcon, 'var(--col-info'),
              disabled: targetUserIsCurrentUser.value,
              action: () => emit('setSuperuserClick', props.targetUser, true),
            },
          ]),
    ],
  },
  {
    type: 'divider',
    key: 'divider',
  },
  {
    label: $t('admin.users.userItemActions.deleteUser'),
    key: 'deleteUser',
    icon: renderIcon(DeleteIcon),
    disabled: targetUserIsCurrentUser.value,
    action: () => emit('deleteClick', props.targetUser),
  },
]);

function handleActionSelect(o: DropdownOption & { action?: () => void }) {
  o.action?.();
}
</script>

<template>
  <n-list-item class="user-list-item">
    <n-thing description-style="font-size: var(--font-size-tiny);" content-indented>
      <template #avatar>
        <user-avatar :avatar-url="targetUser.avatarUrl || undefined" :size="64" />
      </template>
      <template #header>
        <n-flex align="center">
          <router-link :to="{ name: 'user', params: { username: targetUser.username } }" class="b">
            {{ targetUser.name }}
          </router-link>
          <n-badge
            :type="targetUser.isActive ? 'success' : 'error'"
            :processing="!targetUser.isActive"
            :title="targetUser.isActive ? $t('models.user.isActive') : $t('models.user.isInactive')"
            :offset="[12, -2]"
          >
            <template #value>
              <n-icon
                :component="targetUser.isActive ? CheckCircleIcon : BlockCircleIcon"
                color="#fff"
              />
            </template>
          </n-badge>
          <n-badge
            :type="targetUser.isVerified ? 'success' : 'warning'"
            :processing="!targetUser.isVerified"
            :title="
              targetUser.isVerified ? $t('models.user.isVerified') : $t('models.user.isUnverified')
            "
            :offset="[12, -2]"
          >
            <template #value>
              <n-icon :component="VerifiedUserIcon" color="#fff" />
            </template>
          </n-badge>
          <n-badge
            v-if="targetUser.isSuperuser"
            type="info"
            :title="$t('models.user.isSuperuser')"
            :offset="[12, -2]"
          >
            <template #value>
              <n-icon :component="StarIcon" color="#fff" />
            </template>
          </n-badge>
        </n-flex>
      </template>
      <template #header-extra>
        <n-flex>
          <n-dropdown
            :options="actionOptions"
            to="#app-container"
            trigger="click"
            @select="(_, o) => handleActionSelect(o)"
          >
            <n-button quaternary circle :focusable="false">
              <template #icon>
                <n-icon :component="MoreIcon" />
              </template>
            </n-button>
          </n-dropdown>
        </n-flex>
      </template>
      <template #description>
        <span class="translucent"> @{{ targetUser.username }} </span>
      </template>
      <template #default>
        <div class="text-small">
          {{ targetUser.affiliation }}
          –
          <a
            :href="emailLink"
            :title="$t('admin.users.mailtoLinkTitle', { username: targetUser.username })"
          >
            {{ targetUser.email }}
          </a>
          –
          {{ $t('admin.users.registeredAt') }}
          <n-time :time="utcToLocalTime(targetUser.createdAt)" type="datetime" />
        </div>
      </template>
    </n-thing>
  </n-list-item>
</template>

<style>
.user-list-item:first-child {
  padding-top: 0;
}
.user-list-item:last-child {
  padding-bottom: 0;
}
</style>
