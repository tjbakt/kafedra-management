<script setup lang="ts">
import Button from 'primevue/button'
import ProgressBar from 'primevue/progressbar'
import Tag from 'primevue/tag'

import BaseCard from '@/components/base/BaseCard.vue'
import BasePageHeader from '@/components/base/BasePageHeader.vue'
import { useAppConfirm } from '@/composables/useAppConfirm'
import { useAppToast } from '@/composables/useAppToast'

import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const toast = useAppToast()
const { confirmAction } = useAppConfirm()

const { t } = useI18n()

const statistics = computed(() => [
  {
    title: t('dashboard.teachers'),
    value: 42,
    change: t('dashboard.teachersChange'),
    icon: 'pi pi-users',
    route: '/teachers',
  },
  {
    title: t('dashboard.disciplines'),
    value: 86,
    change: t('dashboard.activePlans'),
    icon: 'pi pi-book',
    route: '/disciplines',
  },
  {
    title: t('dashboard.groups'),
    value: 28,
    change: t('dashboard.studentsCount'),
    icon: 'pi pi-id-card',
    route: '/students',
  },
  {
    title: t('dashboard.totalWorkload'),
    value: '18 640',
    suffix: t('dashboard.hours'),
    change: t('dashboard.currentYear'),
    icon: 'pi pi-chart-bar',
    route: '/workload',
  },
])

const workloadItems = computed(() => [
  {
    title: t('dashboard.distributed'),
    value: 82,
    status: t('dashboard.inProgress'),
    severity: 'info' as const,
  },
  {
    title: t('dashboard.checked'),
    value: 64,
    status: t('dashboard.requiresCheck'),
    severity: 'warn' as const,
  },
  {
    title: t('dashboard.approved'),
    value: 48,
    status: t('dashboard.processing'),
    severity: 'success' as const,
  },
])

function showSuccess(): void {
  toast.success(
    t('dashboard.interfaceWorks'),
    t('dashboard.toastConnected'),
  )
}

function showConfirmation(): void {
  confirmAction(
    t('dashboard.confirmDemoAction'),
    () => {
      toast.success(
        t('dashboard.actionConfirmed'),
      )
    },
  )
}
</script>

<template>
  <div class="dashboard">
    <BasePageHeader
      :title="t('dashboard.title')"
      :description="t('dashboard.description')"
      icon="pi pi-home"
    >
      <template #actions>
        <Button
          :label="t('dashboard.showToast')"
          icon="pi pi-bell"
          severity="secondary"
          outlined
          @click="showSuccess"
        />

        <Button
          :label="t('dashboard.checkDialog')"
          icon="pi pi-check-circle"
          @click="showConfirmation"
        />
      </template>
    </BasePageHeader>

    <div class="statistics-grid">
      <RouterLink
        v-for="item in statistics"
        :key="item.title"
        :to="item.route"
        class="statistic-card"
      >
        <div class="statistic-card__header">
          <span class="statistic-card__icon">
            <i :class="item.icon" />
          </span>

          <i class="pi pi-arrow-up-right statistic-card__arrow" />
        </div>

        <div class="statistic-card__value">
          {{ item.value }}
          <small v-if="item.suffix">{{ item.suffix }}</small>
        </div>

        <strong>{{ item.title }}</strong>
        <span>{{ item.change }}</span>
      </RouterLink>
    </div>

    <div class="dashboard-grid">
      <BaseCard
        :title="t('dashboard.workloadDistribution')"
        :subtitle="
          t('dashboard.workloadDistributionDescription')
        "
      >
        <template #actions>
          <Button
            :label="t('dashboard.openModule')"
            icon="pi pi-arrow-right"
            icon-pos="right"
            size="small"
            text
            as="router-link"
            to="/workload"
          />
        </template>

        <div class="workload-list">
          <div v-for="item in workloadItems" :key="item.title" class="workload-item">
            <div class="workload-item__header">
              <div>
                <strong>{{ item.title }}</strong>
                <span>{{ item.value }}%</span>
              </div>

              <Tag :value="item.status" :severity="item.severity" />
            </div>

            <ProgressBar :value="item.value" :show-value="false" class="workload-item__progress" />
          </div>
        </div>
      </BaseCard>

      <BaseCard :title="t('dashboard.quickActions')" :subtitle="t('dashboard.quickActionsDescription')">
        <div class="quick-actions">
          <RouterLink to="/teachers" class="quick-action">
            <i class="pi pi-user-plus" />
            <span>
              <strong>{{ t('dashboard.teachers') }}</strong>
              <small>{{t('dashboard.teachersChange')}}</small>
            </span>
            <i class="pi pi-chevron-right" />
          </RouterLink>

          <RouterLink to="/curriculum" class="quick-action">
            <i class="pi pi-list-check" />
            <span>
              <strong>{{t('dashboard.disciplines')}}</strong>
              <small>{{t('dashboard.activePlans')}}</small>
            </span>
            <i class="pi pi-chevron-right" />
          </RouterLink>

          <RouterLink to="/workload" class="quick-action">
            <i class="pi pi-chart-bar" />
            <span>
              <strong>{{ t('dashboard.totalWorkload') }}</strong>
              <small>{{t('dashboard.currentYear')}}</small>
            </span>
            <i class="pi pi-chevron-right" />
          </RouterLink>

          <RouterLink to="/reports" class="quick-action">
            <i class="pi pi-file-export" />
            <span>
              <strong>{{ t('navigation.reports') }}</strong>
              <small>{{t('dashboard.pdfAndExcel')}}</small>
            </span>
            <i class="pi pi-chevron-right" />
          </RouterLink>
        </div>
      </BaseCard>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  display: grid;
  gap: 1.25rem;
}

.statistics-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1rem;
}

.statistic-card {
  display: grid;
  gap: 0.25rem;
  padding: 1.15rem;
  border: 1px solid var(--app-border-color);
  border-radius: var(--app-radius-lg);
  background: var(--app-surface);
  box-shadow: var(--app-shadow-sm);
  color: inherit;
  text-decoration: none;
  transition:
    transform var(--app-transition),
    box-shadow var(--app-transition),
    border-color var(--app-transition);
}

.statistic-card:hover {
  border-color: color-mix(in srgb, var(--app-primary) 45%, var(--app-border-color));
  box-shadow: var(--app-shadow);
  transform: translateY(-2px);
}

.statistic-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.statistic-card__icon {
  display: grid;
  width: 2.6rem;
  height: 2.6rem;
  place-items: center;
  border-radius: 0.75rem;
  background: color-mix(in srgb, var(--app-primary) 12%, transparent);
  color: var(--app-primary);
}

.statistic-card__arrow {
  color: var(--app-text-soft);
  font-size: 0.75rem;
}

.statistic-card__value {
  margin-top: 0.85rem;
  font-size: 1.75rem;
  font-weight: 700;
}

.statistic-card__value small {
  color: var(--app-text-muted);
  font-size: 0.75rem;
  font-weight: 500;
}

.statistic-card > strong {
  font-size: 0.82rem;
}

.statistic-card > span {
  color: var(--app-text-muted);
  font-size: 0.72rem;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.5fr) minmax(20rem, 0.8fr);
  gap: 1rem;
}

.workload-list {
  display: grid;
  gap: 1.3rem;
}

.workload-item {
  display: grid;
  gap: 0.65rem;
}

.workload-item__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.workload-item__header > div {
  display: flex;
  align-items: baseline;
  gap: 0.6rem;
}

.workload-item__header strong {
  font-size: 0.85rem;
}

.workload-item__header span {
  color: var(--app-text-muted);
  font-size: 0.75rem;
}

.workload-item__progress {
  height: 0.45rem;
}

.quick-actions {
  display: grid;
  gap: 0.4rem;
}

.quick-action {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 0.75rem;
  border-radius: 0.7rem;
  color: inherit;
  text-decoration: none;
}

.quick-action:hover {
  background: var(--app-hover-bg);
}

.quick-action > i:first-child {
  display: grid;
  width: 2.25rem;
  height: 2.25rem;
  flex: 0 0 2.25rem;
  place-items: center;
  border-radius: 0.65rem;
  background: color-mix(in srgb, var(--app-primary) 10%, transparent);
  color: var(--app-primary);
}

.quick-action > span {
  display: grid;
  flex: 1;
  gap: 0.15rem;
}

.quick-action strong {
  font-size: 0.82rem;
}

.quick-action small,
.quick-action > i:last-child {
  color: var(--app-text-muted);
  font-size: 0.72rem;
}

@media (max-width: 1199px) {
  .statistics-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 991px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 575px) {
  .statistics-grid {
    grid-template-columns: 1fr;
  }
}
</style>
