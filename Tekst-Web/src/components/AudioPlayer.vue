<script setup lang="ts">
import { DownloadIcon, ErrorIcon, LinkIcon, PauseIcon, PlayIcon } from '@/icons';
import { useMediaControls } from '@vueuse/core';
import { NButton, NFlex, NIcon, NSlider } from 'naive-ui';
import { computed, onMounted, ref, watch, type CSSProperties } from 'vue';

const props = defineProps<{
  src: string;
  externalLink?: string;
  caption?: string;
  instanceId?: string;
  fontStyle?: CSSProperties;
  compact?: boolean;
}>();
defineExpose({ play, pause });
const emit = defineEmits(['play', 'ended']);

const audioRef = ref<HTMLAudioElement>();
const error = ref(false);
const { playing, waiting, currentTime, duration, ended, onSourceError, onPlaybackError } =
  useMediaControls(audioRef, {
    src: props.src,
  });

const secondsToTimeString = (seconds: number) => {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return m + ':' + `${s}`.padStart(2, '0');
};

const currentTimeString = computed(() => secondsToTimeString(currentTime.value || 0));
const durationString = computed(() => secondsToTimeString(duration.value || 0));

function playPause() {
  if (!playing.value) play();
  else pause();
}

function play(reset?: boolean) {
  if (reset) currentTime.value = 0;
  playing.value = true;
  emit('play', props.instanceId);
}

function pause() {
  playing.value = false;
}

function download() {
  window.open(props.src, '_blank', 'noopener noreferrer');
}

function openTab(url: string) {
  window.open(url, '_blank', 'noopener noreferrer');
}

watch(ended, (after) => {
  if (after) emit('ended', props.instanceId);
});

onMounted(() => {
  onSourceError(() => {
    playing.value = false;
    error.value = true;
  });
  onPlaybackError(() => {
    playing.value = false;
    error.value = true;
  });
});
</script>

<template>
  <n-flex vertical class="audio-player" :style="{ flexBasis: compact ? 'unset' : '100%' }">
    <audio ref="audioRef" preload="metadata"></audio>
    <n-flex align="center" flex>
      <n-button
        :secondary="!playing"
        :type="error ? 'error' : 'primary'"
        :focusable="false"
        :disabled="waiting || error"
        :loading="waiting && !error"
        :title="compact ? caption : undefined"
        @click="playPause"
      >
        <template #icon>
          <n-icon v-if="error" :component="ErrorIcon" />
          <n-icon v-else-if="playing" :component="PauseIcon" />
          <n-icon v-else :component="PlayIcon" />
        </template>
      </n-button>
      <div v-if="!compact" class="text-tiny">{{ currentTimeString }} / {{ durationString }}</div>
      <n-flex v-if="!compact" align="center" :wrap="false" style="width: auto; flex: 2 200px">
        <n-slider
          v-model:value="currentTime"
          :step="1"
          :min="0"
          :max="duration"
          :format-tooltip="(seconds) => secondsToTimeString(seconds)"
          :disabled="error"
          style="width: auto; flex: 2 200px"
        />
        <n-button
          v-if="externalLink"
          quaternary
          circle
          size="small"
          :focusable="false"
          @click="openTab(externalLink)"
        >
          <template #icon>
            <n-icon :component="LinkIcon" />
          </template>
        </n-button>
        <n-button
          quaternary
          circle
          size="small"
          :focusable="false"
          :disabled="error"
          @click="download"
        >
          <template #icon>
            <n-icon :component="DownloadIcon" />
          </template>
        </n-button>
      </n-flex>
    </n-flex>
    <div
      v-if="caption && !compact"
      class="pre-wrap text-tiny translucent"
      :class="{ translucent: error }"
      :style="fontStyle"
    >
      {{ caption }}
    </div>
  </n-flex>
</template>

<style scoped>
.audio-player {
  padding: 8px 0;
}
</style>
