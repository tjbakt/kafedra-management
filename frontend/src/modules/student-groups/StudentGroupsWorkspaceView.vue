<script setup lang="ts">
import Tab from 'primevue/tab'
import TabList from 'primevue/tablist'
import TabPanel from 'primevue/tabpanel'
import TabPanels from 'primevue/tabpanels'
import Tabs from 'primevue/tabs'

import {
  ref,
} from 'vue'

import {
  useI18n,
} from 'vue-i18n'

import StudentGroupsView
  from '@/modules/student-groups/StudentGroupsView.vue'

import TeachingSetupView
  from '@/modules/teaching-setup/TeachingSetupView.vue'

const { t } =
  useI18n()

const activeTab =
  ref('groups')
</script>

<template>
  <Tabs
    v-model:value="
      activeTab
    "
  >
    <TabList>
      <Tab value="groups">
        {{
          t(
            'navigation.studentGroups',
          )
        }}
      </Tab>

      <Tab value="setup">
        {{
          t(
            'navigation.teachingSetup',
          )
        }}
      </Tab>
    </TabList>

    <TabPanels>
      <TabPanel value="groups">
        <StudentGroupsView />
      </TabPanel>

      <TabPanel value="setup">
        <TeachingSetupView />
      </TabPanel>
    </TabPanels>
  </Tabs>
</template>
