<script setup lang="ts">
import type { UserRead, UserUpdate } from '@/openapi';
import { NIcon, NTime, NListItem, NThing, NSpace, NButton, useDialog } from 'naive-ui';
import { useI18n } from 'vue-i18n';

import StarRound from '@vicons/material/StarRound';
import VerifiedUserRound from '@vicons/material/VerifiedUserRound';
import BlockRound from '@vicons/material/BlockRound';
import PersonRound from '@vicons/material/PersonRound';
import CheckCircleRound from '@vicons/material/CheckCircleRound';
import QuestionMarkRound from '@vicons/material/QuestionMarkRound';
import { useApi } from '@/api';
import { useMessages } from '@/messages';

defineProps<{
  data: UserRead;
}>();

const emit = defineEmits(['userUpdated']);

const { t } = useI18n({ useScope: 'global' });
const dialog = useDialog();
const { usersApi, authApi } = useApi();
const statusBtnWidth = '128px';
const { message } = useMessages();

async function updateUser(user: UserRead, updates: UserUpdate) {
  try {
    const updatedUser = (await usersApi.usersPatchUser({ id: user.id, userUpdate: updates })).data;
    emit('userUpdated', updatedUser);
    return updatedUser;
  } catch {
    message.error(t('errors.unexpected'));
  }
}

function handleSuperuserClick(user: UserRead) {
  dialog.warning({
    title: t('general.warning'),
    content: user.isSuperuser
      ? t('admin.users.confirmMsg.setUser', { username: user.username })
      : t('admin.users.confirmMsg.setSuperuser', { username: user.username }),
    positiveText: t('general.yesAction'),
    negativeText: t('general.noAction'),
    style: 'font-weight: var(--app-ui-font-weight-light)',
    onPositiveClick: () => updateUser(user, { isSuperuser: !user.isSuperuser }),
  });
}

function handleActiveClick(user: UserRead) {
  dialog.warning({
    title: t('general.warning'),
    content: user.isActive
      ? t('admin.users.confirmMsg.setInactive', { username: user.username })
      : t('admin.users.confirmMsg.setActive', { username: user.username }),
    positiveText: t('general.yesAction'),
    negativeText: t('general.noAction'),
    style: 'font-weight: var(--app-ui-font-weight-light)',
    onPositiveClick: async () => {
      try {
        const updatedUser = await updateUser(user, { isActive: !user.isActive });
        // if just activated but still unverified, send verification mail
        if (updatedUser && updatedUser.isActive && !updatedUser.isVerified) {
          try {
            await authApi.verifyRequestToken({
              bodyVerifyRequestTokenAuthRequestVerifyTokenPost: { email: updatedUser.email },
            });
            message.info(
              t('admin.users.msgSentVerificationLink', { username: updatedUser.username })
            );
          } catch {
            message.error(t('admin.users.msgSentVerificationLinkError'));
          }
        }
      } catch {
        message.error('errors.unexpected');
      }
    },
  });
}

function handleVerifiedClick(user: UserRead) {
  dialog.warning({
    title: t('general.warning'),
    content: user.isVerified
      ? t('admin.users.confirmMsg.setUnverified', { username: user.username })
      : t('admin.users.confirmMsg.setVerified', { username: user.username }),
    positiveText: t('general.yesAction'),
    negativeText: t('general.noAction'),
    style: 'font-weight: var(--app-ui-font-weight-light)',
    onPositiveClick: async () => {
      try {
        const updatedUser = await updateUser(user, { isVerified: !user.isVerified });
        if (updatedUser && !updatedUser.isVerified) {
          try {
            await authApi.verifyRequestToken({
              bodyVerifyRequestTokenAuthRequestVerifyTokenPost: { email: updatedUser.email },
            });
            message.info(
              t('admin.users.msgSentVerificationLink', { username: updatedUser.username })
            );
          } catch {
            message.error(t('admin.users.msgSentVerificationLinkError'));
          }
        }
      } catch {
        message.error('errors.unexpected');
      }
    },
  });
}
</script>

<template>
  <n-list-item>
    <n-thing
      :title="data.username"
      description-style="font-size: var(--app-ui-font-size-tiny); opacity: .6;"
      content-style="margin-top: 8px"
    >
      <template #description>
        {{ data.email }} – {{ t('admin.users.registeredAt') }}
        <n-time :time="new Date(data.createdAt)" type="date" />
      </template>
      <template #header-extra>
        <n-space size="small">
          <!-- isSuperuser -->
          <n-button
            strong
            secondary
            :type="data.isSuperuser ? 'info' : 'default'"
            :title="
              data.isSuperuser
                ? t('admin.users.statusBtnTitle.setUser', { username: data.username })
                : t('admin.users.statusBtnTitle.setSuperuser', { username: data.username })
            "
            size="tiny"
            :style="{ minWidth: statusBtnWidth }"
            @click="handleSuperuserClick(data)"
          >
            {{ data.isSuperuser ? t('models.user.isSuperuser') : t('models.user.modelLabel') }}
            <template #icon>
              <n-icon :component="data.isSuperuser ? StarRound : PersonRound" />
            </template>
          </n-button>
          <!-- isActive -->
          <n-button
            strong
            secondary
            :type="data.isActive ? 'success' : 'error'"
            :title="
              data.isActive
                ? t('admin.users.statusBtnTitle.setInactive', { username: data.username })
                : t('admin.users.statusBtnTitle.setActive', { username: data.username })
            "
            size="tiny"
            :style="{ minWidth: statusBtnWidth }"
            @click="handleActiveClick(data)"
          >
            {{ data.isActive ? t('models.user.isActive') : t('models.user.isInactive') }}
            <template #icon>
              <n-icon :component="data.isActive ? CheckCircleRound : BlockRound" />
            </template>
          </n-button>
          <!-- isVerified -->
          <n-button
            strong
            secondary
            :type="data.isVerified ? 'success' : 'warning'"
            :title="
              data.isVerified
                ? t('admin.users.statusBtnTitle.setUnverified', { username: data.username })
                : t('admin.users.statusBtnTitle.setVerified', { username: data.username })
            "
            size="tiny"
            :style="{ minWidth: statusBtnWidth }"
            @click="handleVerifiedClick(data)"
          >
            {{ data.isVerified ? t('models.user.isVerified') : t('models.user.isUnverified') }}
            <template #icon>
              <n-icon :component="data.isVerified ? VerifiedUserRound : QuestionMarkRound" />
            </template>
          </n-button>
        </n-space>
      </template>
      <div style="font-size: var(--app-ui-font-size-small)">
        {{ data.firstName }} {{ data.lastName }} ({{ data.affiliation }})
      </div>
    </n-thing>
  </n-list-item>
</template>
