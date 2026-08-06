<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import Button from 'primevue/button'
import Checkbox from 'primevue/checkbox'
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'

import BaseFormField from '@/components/base/BaseFormField.vue'
import { useAppToast } from '@/composables/useAppToast'

import { useI18n } from 'vue-i18n'

const router = useRouter()
const { t } = useI18n()
const toast = useAppToast()

const loading = ref(false)

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
  } else if (form.password.length < 4) {
    errors.password =
      t('auth.passwordMinLength')
  }

  return !errors.username && !errors.password
}

async function submit(): Promise<void> {
  if (!validate()) {
    return
  }

  loading.value = true

  try {
    await new Promise((resolve) => window.setTimeout(resolve, 600))

    localStorage.setItem('access_token', 'demo-access-token')

    toast.success(
      t('auth.loginSuccess'),
      t('auth.demoLoginSuccess'),
    )

    await router.push('/')
  } finally {
    loading.value = false
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
        <p>{{ t('auth.loginDescription') }}</p>
      </div>

      <form class="login-form" novalidate @submit.prevent="submit">
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
            :feedback="false"
            toggle-mask
          />
        </BaseFormField>

        <div class="login-form__options">
          <label class="remember-control">
            <Checkbox v-model="form.remember" input-id="remember" binary />
            <span>{{ t('auth.rememberMe') }}</span>
          </label>

          <button
            type="button"
            class="login-form__link"
            @click="
              toast.info(
                '{{ t(\'auth.forgotPassword\') }}',
                'Функция будет подключена после реализации авторизации.',
              )
            "
          >
            Забыли пароль?
          </button>
        </div>

        <Button
          type="submit"
          :label="t('auth.login')"
          icon="pi pi-sign-in"
          class="w-full"
          :loading="loading"
        />
      </form>

      <p class="login-card__demo">{{ t('auth.demoCredentials') }}</p>
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
  background: color-mix(in srgb, var(--app-surface) 94%, transparent);
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

.login-card__demo {
  margin: 1.25rem 0 0;
  color: var(--app-text-muted);
  font-size: 0.72rem;
  line-height: 1.5;
  text-align: center;
}
</style>
