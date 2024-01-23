<script setup lang="ts">
import type { UserRead } from '@/api';
import { NIcon, NTime, NListItem, NThing, NSpace, NButton } from 'naive-ui';
import { usePlatformData } from '@/composables/platformData';

import {
  AdminIcon,
  VerifiedUserIcon,
  BlockIcon,
  UserIcon,
  CheckCircleIcon,
  QuestionMarkIcon,
  ClearIcon,
} from '@/icons';

defineProps<{
  targetUser: UserRead;
  currentUser?: UserRead;
}>();

defineEmits(['superuserClick', 'activeClick', 'verifiedClick', 'deleteClick']);

const { pfData } = usePlatformData();

const statusBtnMinWidth = '128px';
</script>

<template>
  <n-list-item>
    <n-thing
      :title="targetUser.username"
      description-style="font-size: var(--app-ui-font-size-tiny);"
      content-style="margin-top: 8px"
    >
      <template #description>
        <a
          :href="`mailto:${targetUser.email}?subject=${$t('admin.users.mailtoSubject', {
            platform: pfData?.settings.infoPlatformName,
          })}`"
          :title="$t('admin.users.mailtoLinkTitle', { username: targetUser.username })"
        >
          {{ targetUser.email }}
        </a>
        – {{ $t('admin.users.registeredAt') }}
        <n-time :time="new Date(targetUser.createdAt)" type="date" />
      </template>
      <template #header-extra>
        <n-space size="small">
          <!-- isSuperuser -->
          <n-button
            strong
            secondary
            :type="targetUser.isSuperuser ? 'info' : 'default'"
            :title="
              targetUser.isSuperuser
                ? $t('admin.users.statusBtnTitle.setUser', { username: targetUser.username })
                : $t('admin.users.statusBtnTitle.setSuperuser', { username: targetUser.username })
            "
            size="tiny"
            :style="{ minWidth: statusBtnMinWidth }"
            :disabled="currentUser && currentUser.id === targetUser.id"
            @click="$emit('superuserClick', targetUser)"
          >
            {{
              targetUser.isSuperuser ? $t('models.user.isSuperuser') : $t('models.user.modelLabel')
            }}
            <template #icon>
              <n-icon :component="targetUser.isSuperuser ? AdminIcon : UserIcon" />
            </template>
          </n-button>
          <!-- isActive -->
          <n-button
            strong
            secondary
            :type="targetUser.isActive ? 'success' : 'error'"
            :title="
              targetUser.isActive
                ? $t('admin.users.statusBtnTitle.setInactive', { username: targetUser.username })
                : $t('admin.users.statusBtnTitle.setActive', { username: targetUser.username })
            "
            size="tiny"
            :style="{ minWidth: statusBtnMinWidth }"
            :disabled="currentUser && currentUser.id === targetUser.id"
            @click="$emit('activeClick', targetUser)"
          >
            {{ targetUser.isActive ? $t('models.user.isActive') : $t('models.user.isInactive') }}
            <template #icon>
              <n-icon :component="targetUser.isActive ? CheckCircleIcon : BlockIcon" />
            </template>
          </n-button>
          <!-- isVerified -->
          <n-button
            strong
            secondary
            :type="targetUser.isVerified ? 'success' : 'warning'"
            :title="
              targetUser.isVerified
                ? $t('admin.users.statusBtnTitle.setUnverified', { username: targetUser.username })
                : $t('admin.users.statusBtnTitle.setVerified', { username: targetUser.username })
            "
            size="tiny"
            :style="{ minWidth: statusBtnMinWidth }"
            :disabled="currentUser && currentUser.id === targetUser.id"
            @click="$emit('verifiedClick', targetUser)"
          >
            {{
              targetUser.isVerified ? $t('models.user.isVerified') : $t('models.user.isUnverified')
            }}
            <template #icon>
              <n-icon :component="targetUser.isVerified ? VerifiedUserIcon : QuestionMarkIcon" />
            </template>
          </n-button>
          <!-- delete user -->
          <n-button
            strong
            secondary
            type="error"
            :title="$t('admin.users.statusBtnTitle.deleteUser', { username: targetUser.username })"
            size="tiny"
            :disabled="currentUser && currentUser.id === targetUser.id"
            @click="$emit('deleteClick', targetUser)"
          >
            <template #icon>
              <n-icon :component="ClearIcon" />
            </template>
          </n-button>
        </n-space>
      </template>
      <div style="font-size: var(--app-ui-font-size-small)">
        {{ targetUser.name }} ({{ targetUser.affiliation }})
      </div>
    </n-thing>
  </n-list-item>
</template>
