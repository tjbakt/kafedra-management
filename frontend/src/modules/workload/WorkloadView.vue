<script setup lang="ts">
import Tab from 'primevue/tab'
import TabList from 'primevue/tablist'
import TabPanel from 'primevue/tabpanel'
import TabPanels from 'primevue/tabpanels'
import Tabs from 'primevue/tabs'

import {
  useI18n,
} from 'vue-i18n'

import PlannedWorkloadView
  from '@/modules/teaching-workload/components/PlannedWorkloadView.vue'

import WorkloadDistributionView
  from '@/modules/workload-distribution/WorkloadDistributionView.vue'

const { t } = useI18n()
</script>

<template>
  <Tabs value="planned">
    <TabList>
      <Tab value="planned">
        {{
          t(
            'workload.tabs.planned',
          )
        }}
      </Tab>

      <Tab value="distribution">
        {{
          t(
            'workload.tabs.distribution',
          )
        }}
      </Tab>
    </TabList>

    <TabPanels>
      <TabPanel value="planned">
        <PlannedWorkloadView />
      </TabPanel>

      <TabPanel value="distribution">
        <WorkloadDistributionView />
      </TabPanel>
    </TabPanels>
  </Tabs>
</template>
