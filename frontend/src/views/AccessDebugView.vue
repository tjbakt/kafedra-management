<script setup lang="ts">
import Tag from 'primevue/tag'
import { useI18n } from 'vue-i18n'

import BaseCard from '@/components/base/BaseCard.vue'
import BaseEmptyState from '@/components/base/BaseEmptyState.vue'
import BasePageHeader from '@/components/base/BasePageHeader.vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const { t } = useI18n()
</script>

<template>
  <div>
    <BasePageHeader
      :title="
        t('access.debugTitle')
      "
      :description="
        t('access.debugDescription')
      "
      icon="pi pi-shield"
    />

    <div class="access-grid">
      <BaseCard
        :title="
          t('access.userInformation')
        "
      >
        <dl class="access-info">
          <div>
            <dt>
              {{ t('auth.username') }}
            </dt>

            <dd>
              {{
                authStore.user
                  ?.username
              }}
            </dd>
          </div>

          <div>
            <dt>
              Staff
            </dt>

            <dd>
              <Tag
                :value="
                  authStore.user
                    ?.is_staff
                    ? t('common.yes')
                    : t('common.no')
                "
                :severity="
                  authStore.user
                    ?.is_staff
                    ? 'success'
                    : 'secondary'
                "
              />
            </dd>
          </div>
        </dl>
      </BaseCard>

      <BaseCard
        :title="
          t('access.groups')
        "
      >
        <div
          v-if="
            authStore.user
              ?.groups.length
          "
          class="tag-list"
        >
          <Tag
            v-for="
              group in
                authStore.user
                  ?.groups
            "
            :key="group"
            :value="group"
            severity="info"
          />
        </div>

        <BaseEmptyState
          v-else
          icon="pi pi-users"
          :title="
            t(
              'access.noGroups',
            )
          "
          :description="
            t(
              'access.noGroupsDescription',
            )
          "
        />
      </BaseCard>

      <BaseCard
        :title="
          t('access.permissions')
        "
      >
        <div
          v-if="
            authStore.user
              ?.permissions.length
          "
          class="permissions-list"
        >
          <code
            v-for="
              permission in
                authStore.user
                  ?.permissions
            "
            :key="permission"
          >
            {{ permission }}
          </code>
        </div>

        <BaseEmptyState
          v-else
          icon="pi pi-lock"
          :title="
            t(
              'access.noPermissions',
            )
          "
          :description="
            t(
              'access.noPermissionsDescription',
            )
          "
        />
      </BaseCard>
    </div>
  </div>
</template>

<style scoped>
.access-grid {
  display: grid;
  gap: 1rem;
}

.access-info {
  display: grid;
  gap: 0;
  margin: 0;
}

.access-info > div {
  display: grid;
  grid-template-columns:
    minmax(10rem, 0.4fr)
    1fr;
  gap: 1rem;
  padding: 0.75rem 0;
  border-bottom:
    1px solid
    var(--app-border-color);
}

.access-info > div:last-child {
  border-bottom: 0;
}

.access-info dt {
  color:
    var(--app-text-muted);
  font-size: 0.8rem;
}

.access-info dd {
  margin: 0;
  font-size: 0.82rem;
  font-weight: 600;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.permissions-list {
  display: grid;
  grid-template-columns:
    repeat(
      auto-fill,
      minmax(17rem, 1fr)
    );
  gap: 0.5rem;
}

.permissions-list code {
  padding: 0.65rem 0.8rem;
  border:
    1px solid
    var(--app-border-color);
  border-radius: 0.5rem;
  background:
    var(--app-surface-soft);
  color:
    var(--app-text);
  font-size: 0.75rem;
}

@media (max-width: 575px) {
  .access-info > div {
    grid-template-columns: 1fr;
    gap: 0.3rem;
  }
}
</style>
