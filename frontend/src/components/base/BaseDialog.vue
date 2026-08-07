<script setup lang="ts">
import Dialog from 'primevue/dialog'

const visible = defineModel<boolean>({
  default: false,
})

withDefaults(
  defineProps<{
    title: string

    width?: string

    modal?: boolean
    maximizable?: boolean
    dismissableMask?: boolean
    closeOnEscape?: boolean

    loading?: boolean
  }>(),
  {
    width: '36rem',

    modal: true,
    maximizable: false,
    dismissableMask: false,
    closeOnEscape: true,

    loading: false,
  },
)
</script>

<template>
  <Dialog
    v-model:visible="visible"
    :header="title"
    :modal="modal"
    :maximizable="maximizable"
    :dismissable-mask="
      dismissableMask
    "
    :close-on-escape="
      closeOnEscape
    "
    :closable="!loading"
    :style="{
      width,
    }"
    :breakpoints="{
      '1199px': '70vw',
      '767px': '90vw',
      '575px': '95vw',
    }"
    class="base-dialog"
  >
    <div
      class="base-dialog__content"
      :class="{
        'base-dialog__content--loading':
          loading,
      }"
    >
      <slot />
    </div>

    <template
      v-if="$slots.footer"
      #footer
    >
      <slot name="footer" />
    </template>
  </Dialog>
</template>

<style scoped>
.base-dialog__content {
  position: relative;
}

.base-dialog__content--loading {
  pointer-events: none;
  opacity: 0.7;
}
</style>
