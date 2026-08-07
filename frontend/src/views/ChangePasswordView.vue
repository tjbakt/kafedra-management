<script setup lang="ts">
import Button from 'primevue/button'
import Message from 'primevue/message'
import Password from 'primevue/password'
import { reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'

import { getApiErrorMessage } from '@/api/http'
import BaseFormField from '@/components/base/BaseFormField.vue'
import { useAppToast } from '@/composables/useAppToast'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const toast = useAppToast()
const { t } = useI18n()

const loading = ref(false)
const generalError = ref('')

const form = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: '',
})

const errors = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: '',
})

function validate(): boolean {
  errors.currentPassword = ''
  errors.newPassword = ''
  errors.confirmPassword = ''

  if (!form.currentPassword) {
    errors.currentPassword =
      t('auth.passwordRequired')
  }

  if (!form.newPassword) {
    errors.newPassword =
      t('auth.passwordRequired')
  } else if (form.newPassword.length < 8) {
    errors.newPassword =
      'Пароль должен содержать минимум 8 символов'
  }

  if (
    form.newPassword !== form.confirmPassword
  ) {
    errors.confirmPassword =
      'Пароли не совпадают'
  }

  return !Object.values(errors).some(Boolean)
}

async function submit(): Promise<void> {
  generalError.value = ''

  if (!validate()) {
    return
  }

  loading.value = true

  try {
    await authStore.changePassword({
      current_password: form.currentPassword,
      new_password: form.newPassword,
      new_password_confirmation:
        form.confirmPassword,
    })

    toast.success(
      t('common.success'),
      t('auth.changePassword'),
    )

    await router.replace('/')
  } catch (error) {
    generalError.value = getApiErrorMessage(
      error,
    )
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="change-password-page">
    <section class="change-password-card">
      <span class="change-password-card__icon">
        <i class="pi pi-key" />
      </span>

      <h1>{{ t('auth.changePassword') }}</h1>

      <p>
        {{ t('auth.passwordChangeRequired') }}
      </p>

      <Message
        v-if="generalError"
        severity="error"
        :closable="false"
      >
        {{ generalError }}
      </Message>

      <form
        class="change-password-form"
        @submit.prevent="submit"
      >
        <BaseFormField
          :label="t('auth.currentPassword')"
          name="current-password"
          required
          :error="errors.currentPassword"
        >
          <Password
            input-id="current-password"
            v-model="form.currentPassword"
            class="w-full"
            input-class="w-full"
            :feedback="false"
            toggle-mask
          />
        </BaseFormField>

        <BaseFormField
          :label="t('auth.newPassword')"
          name="new-password"
          required
          :error="errors.newPassword"
        >
          <Password
            input-id="new-password"
            v-model="form.newPassword"
            class="w-full"
            input-class="w-full"
            toggle-mask
          />
        </BaseFormField>

        <BaseFormField
          :label="t('auth.confirmPassword')"
          name="confirm-password"
          required
          :error="errors.confirmPassword"
        >
          <Password
            input-id="confirm-password"
            v-model="form.confirmPassword"
            class="w-full"
            input-class="w-full"
            :feedback="false"
            toggle-mask
          />
        </BaseFormField>

        <Button
          type="submit"
          :label="t('common.save')"
          icon="pi pi-check"
          class="w-full"
          :loading="loading"
        />
      </form>
    </section>
  </div>
</template>

<style scoped>
.change-password-page {
  width: 100%;
  max-width: 30rem;
  margin: 0 auto;
}

.change-password-card {
  display: grid;
  gap: 1rem;
  padding: 2rem;
  border: 1px solid var(--app-border-color);
  border-radius: var(--app-radius-lg);
  background: var(--app-surface);
  box-shadow: var(--app-shadow-lg);
}

.change-password-card__icon {
  display: grid;
  width: 3.5rem;
  height: 3.5rem;
  place-items: center;
  border-radius: 50%;
  background: color-mix(
    in srgb,
    var(--app-primary) 12%,
    transparent
  );
  color: var(--app-primary);
}

.change-password-card__icon i {
  font-size: 1.4rem;
}

.change-password-card h1,
.change-password-card p {
  margin: 0;
}

.change-password-card p {
  color: var(--app-text-muted);
}

.change-password-form {
  display: grid;
  gap: 1rem;
}
</style>
