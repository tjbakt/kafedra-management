<script setup lang="ts">
import Textarea from 'primevue/textarea'

import {
  computed,
  ref,
  watch,
} from 'vue'

import { useI18n } from 'vue-i18n'

import BaseDialog from '@/components/base/BaseDialog.vue'
import BaseFormActions from '@/components/base/BaseFormActions.vue'
import BaseFormField from '@/components/base/BaseFormField.vue'

import type {
  AcademicYear,
} from '@/modules/academic-settings/types'

type Operation =
  | 'close'
  | 'reopen'

const visible =
  defineModel<boolean>({
    default: false,
  })

const props = withDefaults(
  defineProps<{
    academicYear: AcademicYear | null

    operation: Operation

    loading?: boolean
  }>(),
  {
    loading: false,
  },
)

const emit = defineEmits<{
  submit: [value: string]
}>()

const { t } = useI18n()

const text = ref('')
const error = ref('')

const title = computed(
  () =>
    props.operation === 'close'
      ? t(
          'academicSettings.academicYears.closeTitle',
        )
      : t(
          'academicSettings.academicYears.reopenTitle',
        ),
)

const label = computed(
  () =>
    props.operation === 'close'
      ? t(
          'academicSettings.academicYears.fields.closingComment',
        )
      : t(
          'academicSettings.academicYears.fields.reopeningReason',
        ),
)

function submit(): void {
  error.value = ''

  if (
    props.operation === 'reopen' &&
    !text.value.trim()
  ) {
    error.value =
      t(
        'academicSettings.academicYears.validation.reopenReason',
      )

    return
  }

  emit(
    'submit',
    text.value.trim(),
  )
}

watch(
  visible,
  (value) => {
    if (value) {
      text.value = ''
      error.value = ''
    }
  },
)
</script>

<template>
  <BaseDialog
    v-model="visible"
    :title="title"
    width="38rem"
    :loading="loading"
  >
    <p
      v-if="academicYear"
      class="status-dialog__description"
    >
      {{
        operation === 'close'
          ? t(
              'academicSettings.academicYears.closeDescription',
              {
                year:
                  academicYear.name,
              },
            )
          : t(
              'academicSettings.academicYears.reopenDescription',
              {
                year:
                  academicYear.name,
              },
            )
      }}
    </p>

    <BaseFormField
      :label="label"
      name="status_comment"
      :required="
        operation === 'reopen'
      "
      :error="error"
    >
      <Textarea
        v-model="text"
        rows="5"
        maxlength="5000"
        auto-resize
        class="w-full"
      />
    </BaseFormField>

    <template #footer>
      <BaseFormActions
        :loading="loading"
        :save-label="
          operation === 'close'
            ? t(
                'academicSettings.academicYears.close',
              )
            : t(
                'academicSettings.academicYears.reopen',
              )
        "
        :submit-icon="
          operation === 'close'
            ? 'pi pi-lock'
            : 'pi pi-lock-open'
        "
        @cancel="
          visible = false
        "
        @submit="submit"
      />
    </template>
  </BaseDialog>
</template>

<style scoped>
.status-dialog__description {
  margin: 0 0 1rem;
  color:
    var(--app-text-muted);
  line-height: 1.6;
}
</style>
