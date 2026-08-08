<script setup lang="ts">
import Button from 'primevue/button'
import Checkbox from 'primevue/checkbox'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'
import Password from 'primevue/password'
import { reactive } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  useRoute,
  useRouter,
} from 'vue-router'

import BaseFormField from '@/components/base/BaseFormField.vue'
import { useAppToast } from '@/composables/useAppToast'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const toast = useAppToast()
const { t } = useI18n()

const form = reactive({
  username: '',
  password: '',
  remember: false,
})

const errors = reactive({
  username: '',
  password: '',
})

function validate(): boolean {
  errors.username = ''
  errors.password = ''

  if (!form.username.trim()) {
    errors.username =
      t('auth.usernameRequired')
  }

  if (!form.password) {
    errors.password =
      t('auth.passwordRequired')
  }

  return !errors.username && !errors.password
}

async function submit(): Promise<void> {
  authStore.clearLoginError()

  if (!validate()) {
    return
  }

  try {
    const user = await authStore.login({
      username: form.username.trim(),
      password: form.password,
    })

    toast.success(
      t('auth.loginSuccess'),
      t('auth.welcome', {
        name:
          user.full_name || user.username,
      }),
    )

    if (user.must_change_password) {
      await router.replace({
        name: 'change-password',
      })

      return
    }

    const redirect =
      typeof route.query.redirect === 'string'
        ? route.query.redirect
        : '/'

    await router.replace(redirect)
  } catch {
    // Ошибка уже сохранена в authStore.
  }
}
</script>

<template>
  <div class="login-page">
    <section class="login-card">
      <div class="login-card__brand">
        <span class="login-card__logo">
          <i class="pi pi-graduation-cap" />
        </span>

        <div>
          <strong>{{ t('app.name') }}</strong>
          <span>{{ t('app.title') }}</span>
        </div>
      </div>

      <div class="login-card__heading">
        <h1>{{ t('auth.loginTitle') }}</h1>
        <p>
          {{ t('auth.loginDescription') }}
        </p>
      </div>

      <Message
        v-if="authStore.loginError"
        severity="error"
        :closable="false"
        class="login-card__message"
      >
        {{ authStore.loginError }}
      </Message>

      <form
        class="login-form"
        novalidate
        @submit.prevent="submit"
      >
        <BaseFormField
          :label="t('auth.username')"
          name="username"
          required
          :error="errors.username"
        >
          <InputText
            id="username"
            v-model="form.username"
            class="w-full"
            :invalid="Boolean(errors.username)"
            autocomplete="username"
            :disabled="authStore.loading"
            :placeholder="
              t('auth.usernamePlaceholder')
            "
          />
        </BaseFormField>

        <BaseFormField
          :label="t('auth.password')"
          name="password"
          required
          :error="errors.password"
        >
          <Password
            input-id="password"
            v-model="form.password"
            class="w-full"
            input-class="w-full"
            :invalid="Boolean(errors.password)"
            autocomplete="current-password"
            :placeholder="
              t('auth.passwordPlaceholder')
            "
            :disabled="authStore.loading"
            :feedback="false"
            toggle-mask
          />
        </BaseFormField>

        <div class="login-form__options">
          <label class="remember-control">
            <Checkbox
              v-model="form.remember"
              input-id="remember"
              binary
              :disabled="authStore.loading"
            />

            <span>
              {{ t('auth.rememberMe') }}
            </span>
          </label>

          <button
            type="button"
            class="login-form__link"
            :disabled="authStore.loading"
            @click="
              toast.info(
                t('auth.passwordRecovery'),
                t('auth.passwordRecoveryLater'),
              )
            "
          >
            {{ t('auth.forgotPassword') }}
          </button>
        </div>

        <Button
          type="submit"
          :label="
            authStore.loading
              ? t('auth.loggingIn')
              : t('auth.login')
          "
          icon="pi pi-sign-in"
          class="w-full"
          :loading="authStore.loading"
        />
      </form>
    </section>
  </div>
</template>

<style scoped>
.login-page {
  width: 100%;
  max-width: 28rem;
  margin: 0 auto;
}

.login-card {
  padding: clamp(1.5rem, 5vw, 2.3rem);
  border: 1px solid var(--app-border-color);
  border-radius: 1.25rem;
  background: color-mix(
    in srgb,
    var(--app-surface) 94%,
    transparent
  );
  box-shadow: var(--app-shadow-lg);
  backdrop-filter: blur(18px);
}

.login-card__brand {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}

.login-card__logo {
  display: grid;
  width: 3rem;
  height: 3rem;
  place-items: center;
  border-radius: 0.85rem;
  background: var(--app-primary);
  color: white;
}

.login-card__logo i {
  font-size: 1.4rem;
}

.login-card__brand > div {
  display: grid;
  gap: 0.2rem;
}

.login-card__brand strong {
  font-size: 0.94rem;
}

.login-card__brand span {
  color: var(--app-text-muted);
  font-size: 0.72rem;
}

.login-card__heading {
  margin: 2rem 0 1.5rem;
}

.login-card__heading h1 {
  margin: 0;
  font-size: 1.55rem;
}

.login-card__heading p {
  margin: 0.4rem 0 0;
  color: var(--app-text-muted);
  font-size: 0.82rem;
}

.login-card__message {
  margin-bottom: 1rem;
}

.login-form {
  display: grid;
  gap: 1.15rem;
}

.login-form__options {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.remember-control {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.78rem;
  cursor: pointer;
}

.login-form__link {
  padding: 0;
  border: 0;
  background: transparent;
  color: var(--app-primary);
  font-size: 0.78rem;
  cursor: pointer;
}

.login-form__link:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}
</style>
