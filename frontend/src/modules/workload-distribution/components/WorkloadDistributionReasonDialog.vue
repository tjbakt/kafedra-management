<script setup lang="ts">
import Textarea from 'primevue/textarea'

import {
  ref,
  watch,
} from 'vue'

import {
  useI18n,
} from 'vue-i18n'

import BaseDialog from '@/components/base/BaseDialog.vue'
import BaseFormActions from '@/components/base/BaseFormActions.vue'
import BaseFormField from '@/components/base/BaseFormField.vue'

const visible =
  defineModel<boolean>({
    default: false,
  })

const props =
  defineProps<{
    title: string
    loading?: boolean
  }>()

const emit =
  defineEmits<{
    submit: [
      reason: string,
    ]
  }>()

const { t } =
  useI18n()

const reason =
  ref('')

const error =
  ref('')

function submit(): void {
  const value =
    reason.value.trim()

  if (!value) {
    error.value =
      t(
        'workloadDistribution.validation.reasonRequired',
      )

    return
  }

  emit(
    'submit',
    value,
  )
}

watch(
  () => visible.value,
  (value) => {
    if (value) {
      reason.value = ''
      error.value = ''
    }
  },
)
</script>

<template>
  <BaseDialog
    v-model="visible"
    :title="props.title"
    width="36rem"
    :loading="props.loading"
  >
    <BaseFormField
      :label="
        t(
          'workloadDistribution.fields.reason',
        )
      "
      required
      :error="error"
    >
      <Textarea
        v-model="reason"
        rows="5"
        auto-resize
        class="w-full"
      />
    </BaseFormField>

    <template #footer>
      <BaseFormActions
        :loading="loading"
        @submit="submit"
        @cancel="
          visible = false
        "
      />
    </template>
  </BaseDialog>
</template>
