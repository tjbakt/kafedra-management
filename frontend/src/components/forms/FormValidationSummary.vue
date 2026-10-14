<script setup lang="ts">
import Message from 'primevue/message'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import type {
  FieldErrors,
} from '@/types/validation'

import {
  getFieldErrorLabel,
} from '@/utils/api-errors'

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

interface ValidationMessage {
  key: string
  text: string
}

const messages = computed<ValidationMessage[]>(
  () => {
    const result: ValidationMessage[] = []

    /*
     * Общая ошибка показывается только если
     * она действительно не является техническим
     * сообщением Axios.
     */
    if (
      props.generalError &&
      !/^Request failed with status code \d+$/i.test(
        props.generalError.trim(),
      )
    ) {
      result.push({
        key: 'general',
        text: props.generalError.trim(),
      })
    }

    props.nonFieldErrors.forEach(
      (message, index) => {
        const text = message.trim()

        if (!text) {
          return
        }

        result.push({
          key: `non-field-${index}-${text}`,
          text,
        })
      },
    )

    Object.entries(
      props.fieldErrors,
    ).forEach(
      ([field, errors]) => {
        const label =
          getFieldErrorLabel(field)

        errors.forEach(
          (message, index) => {
            const text =
              message.trim()

            if (!text) {
              return
            }

            result.push({
              key: `${field}-${index}-${text}`,
              text: `${label}: ${text}`,
            })
          },
        )
      },
    )

    const seen = new Set<string>()

    return result.filter(
      (item) => {
        if (seen.has(item.text)) {
          return false
        }

        seen.add(item.text)

        return true
      },
    )
  },
)
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
          v-for="message in messages"
          :key="message.key"
        >
          {{ message.text }}
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
