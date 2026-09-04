<script setup lang="ts">
import {
  computed,
  ref,
} from 'vue'

import Tab from 'primevue/tab'
import TabList from 'primevue/tablist'
import TabPanel from 'primevue/tabpanel'
import TabPanels from 'primevue/tabpanels'
import Tabs from 'primevue/tabs'

import UniversityView from '@/modules/organization/UniversityView.vue'
import FacultyView from '@/modules/organization/FacultyView.vue'

import DepartmentView from '@/modules/departments/DepartmentView.vue'

import {
  usePermissions,
} from '@/composables/usePermissions'

const {
  can,
} = usePermissions()

const activeTab =
  ref('0')

const canViewUniversity =
  computed(() =>
    can(
      'organizations.view_university',
    ),
  )

const canViewFaculty =
  computed(() =>
    can(
      'organizations.view_faculty',
    ),
  )

const canViewDepartment =
  computed(() =>
    can(
      'organizations.view_department',
    ),
  )
</script>

<template>
  <div class="organization-page">
    <Tabs v-model:value="activeTab">
      <TabList>
        <Tab
          v-if="canViewUniversity"
          value="0"
        >
          <i class="pi pi-building" />
          <span>ВУЗ</span>
        </Tab>

        <Tab
          v-if="canViewFaculty"
          value="1"
        >
          <i
            class="pi pi-building-columns"
          />
          <span>Факультеты</span>
        </Tab>

        <Tab
          v-if="canViewDepartment"
          value="2"
        >
          <i class="pi pi-sitemap" />
          <span>Кафедры</span>
        </Tab>
      </TabList>

      <TabPanels>
        <TabPanel
          v-if="canViewUniversity"
          value="0"
        >
          <UniversityView />
        </TabPanel>

        <TabPanel
          v-if="canViewFaculty"
          value="1"
        >
          <FacultyView />
        </TabPanel>

        <TabPanel
          v-if="canViewDepartment"
          value="2"
        >
          <DepartmentView />
        </TabPanel>
      </TabPanels>
    </Tabs>
  </div>
</template>

<style scoped>
.organization-page {
  display: grid;
  gap: 1rem;
}

.organization-page :deep(.p-tablist) {
  overflow-x: auto;
}

.organization-page :deep(.p-tab) {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  white-space: nowrap;
}

.organization-page :deep(.p-tabpanels) {
  padding: 1rem 0 0;
}

.organization-page :deep(.organization-list) {
  width: 100%;
}
</style>
