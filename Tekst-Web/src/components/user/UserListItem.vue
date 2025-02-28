<script setup lang="ts">
import type { UserRead } from '@/api';
import UserAvatar from '@/components/user/UserAvatar.vue';
import { $t } from '@/i18n';
import {
  AdminIcon,
  BlockCircleIcon,
  CheckCircleIcon,
  DeleteIcon,
  MoreIcon,
  UserDowngradeIcon,
  VerifiedUserIcon,
} from '@/icons';
import { renderIcon, utcToLocalTime } from '@/utils';
import {
  NBadge,
  NButton,
  NDropdown,
  NFlex,
  NIcon,
  NListItem,
  NThing,
  NTime,
  useThemeVars,
  type DropdownOption,
} from 'naive-ui';
import { computed } from 'vue';
import { RouterLink } from 'vue-router';

const props = defineProps<{
  targetUser: UserRead;
  platformName: string;
  currentUser?: UserRead | null;
}>();

const emit = defineEmits([
  'setSuperuserClick',
  'unsetSuperuserClick',
  'activateClick',
  'verifyClick',
  'deleteClick',
]);

const nuiTheme = useThemeVars();

const targetUserIsCurrentUser = computed(() => props.targetUser.id === props.currentUser?.id);
const emailLink = computed(
  () =>
    `mailto:${props.targetUser.email}?subject=${$t('admin.users.mailtoSubject', {
      platform: props.platformName,
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
              icon: renderIcon(BlockCircleIcon, nuiTheme.value.errorColor),
              disabled: targetUserIsCurrentUser.value,
              action: () => emit('activateClick', props.targetUser, false),
            },
          ]
        : [
            {
              label: $t('admin.users.userItemActions.setActive'),
              key: 'setActive',
              icon: renderIcon(CheckCircleIcon, nuiTheme.value.successColor),
              disabled: targetUserIsCurrentUser.value,
              action: () => emit('activateClick', props.targetUser, true),
            },
          ]),
      ...(props.targetUser.isVerified
        ? [
            {
              label: $t('admin.users.userItemActions.setUnverified'),
              key: 'setUnverified',
              icon: renderIcon(VerifiedUserIcon, nuiTheme.value.warningColor),
              disabled: targetUserIsCurrentUser.value,
              action: () => emit('verifyClick', props.targetUser, false),
            },
          ]
        : [
            {
              label: $t('admin.users.userItemActions.setVerified'),
              key: 'setVerified',
              icon: renderIcon(VerifiedUserIcon, nuiTheme.value.successColor),
              disabled: targetUserIsCurrentUser.value,
              action: () => emit('verifyClick', props.targetUser, true),
            },
          ]),
      ...(props.targetUser.isSuperuser
        ? [
            {
              label: $t('admin.users.userItemActions.unsetSuperuser'),
              key: 'setUser',
              icon: renderIcon(UserDowngradeIcon, nuiTheme.value.errorColor),
              disabled: targetUserIsCurrentUser.value,
              action: () => emit('setSuperuserClick', props.targetUser, false),
            },
          ]
        : [
            {
              label: $t('admin.users.userItemActions.setSuperuser'),
              key: 'setSuperuser',
              icon: renderIcon(AdminIcon, nuiTheme.value.infoColor),
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
    <n-thing content-indented>
      <template #avatar>
        <user-avatar :avatar-url="targetUser.avatarUrl || undefined" :size="64" />
      </template>
      <template #header>
        <n-flex align="center">
          <router-link :to="{ name: 'user', params: { username: targetUser.username } }" class="b">
            {{ targetUser.name }}
          </router-link>
          <span class="translucent text-small"> @{{ targetUser.username }} </span>
          <n-flex size="small" :wrap="false">
            <n-badge
              :color="targetUser.isActive ? nuiTheme.successColor : nuiTheme.errorColor"
              :processing="!targetUser.isActive"
              :title="
                targetUser.isActive ? $t('models.user.isActive') : $t('models.user.isInactive')
              "
              :offset="[12, -2]"
            >
              <template #value>
                <n-icon
                  :component="targetUser.isActive ? CheckCircleIcon : BlockCircleIcon"
                  :color="nuiTheme.baseColor"
                />
              </template>
            </n-badge>
            <n-badge
              :color="targetUser.isVerified ? nuiTheme.successColor : nuiTheme.warningColor"
              :processing="!targetUser.isVerified"
              :title="
                targetUser.isVerified
                  ? $t('models.user.isVerified')
                  : $t('models.user.isUnverified')
              "
              :offset="[12, -2]"
            >
              <template #value>
                <n-icon :component="VerifiedUserIcon" :color="nuiTheme.baseColor" />
              </template>
            </n-badge>
            <n-badge
              v-if="targetUser.isSuperuser"
              :color="nuiTheme.infoColor"
              :title="$t('models.user.isSuperuser')"
              :offset="[12, -2]"
            >
              <template #value>
                <n-icon :component="AdminIcon" :color="nuiTheme.baseColor" />
              </template>
            </n-badge>
          </n-flex>
        </n-flex>
      </template>
      <template #header-extra>
        <n-flex>
          <n-dropdown
            :options="actionOptions"
            trigger="click"
            placement="bottom-end"
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
        <n-flex class="text-small" size="small">
          <a
            :href="emailLink"
            :title="$t('admin.users.mailtoLinkTitle', { username: targetUser.username })"
          >
            {{ targetUser.email }}
          </a>
          <span class="translucent">&bull;</span>
          <span>{{ targetUser.affiliation }}</span>
          <span class="translucent">&bull;</span>
          <span class="translucent">
            {{ $t('admin.users.registeredAt') }}
            <n-time :time="utcToLocalTime(targetUser.createdAt)" type="datetime" />
          </span>
        </n-flex>
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
