<script setup lang="ts">
import Message from 'primevue/message'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import type {
  FieldErrors,
} from '@/types/validation'

const props = withDefaults(
  defineProps<{
    fieldErrors?: FieldErrors
    nonFieldErrors?: string[]
    generalError?: string
  }>(),
  {
    fieldErrors: () => ({}),
    nonFieldErrors: () => [],
    generalError: '',
  },
)

const { t } = useI18n()

const messages = computed(() => {
  const result: string[] = []

  if (props.generalError) {
    result.push(
      props.generalError,
    )
  }

  result.push(
    ...props.nonFieldErrors,
  )

  Object.values(
    props.fieldErrors,
  ).forEach((errors) => {
    result.push(...errors)
  })

  return [
    ...new Set(result),
  ]
})
</script>

<template>
  <Message
    v-if="messages.length"
    severity="error"
    :closable="false"
    class="validation-summary"
  >
    <div>
      <strong>
        {{
          t(
            'crud.validationFailed',
          )
        }}
      </strong>

      <ul>
        <li
          v-for="
            message in messages
          "
          :key="message"
        >
          {{ message }}
        </li>
      </ul>
    </div>
  </Message>
</template>

<style scoped>
.validation-summary {
  margin-bottom: 1rem;
}

.validation-summary strong {
  display: block;
  margin-bottom: 0.4rem;
}

.validation-summary ul {
  margin: 0;
  padding-left: 1.25rem;
}

.validation-summary li {
  margin: 0.2rem 0;
}
</style>
