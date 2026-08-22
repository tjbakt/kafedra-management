<script setup lang="ts">
import Tab from 'primevue/tab'
import TabList from 'primevue/tablist'
import TabPanel from 'primevue/tabpanel'
import TabPanels from 'primevue/tabpanels'
import Tabs from 'primevue/tabs'

import {
  defineAsyncComponent,
  ref,
} from 'vue'

import {
  useI18n,
} from 'vue-i18n'

const PlannedWorkloadView =
  defineAsyncComponent(
    () =>
      import(
        '@/modules/teaching-workload/components/PlannedWorkloadView.vue'
      ),
  )

const WorkloadDistributionView =
  defineAsyncComponent(
    () =>
      import(
        '@/modules/workload-distribution/WorkloadDistributionView.vue'
      ),
  )

type WorkloadTab =
  | 'planned'
  | 'distribution'

const activeTab =
  ref<WorkloadTab>(
    'planned',
  )

const { t } =
  useI18n()
</script>

<template>
  <div
    class="
      workload-view
    "
  >
    <Tabs
      v-model:value="
        activeTab
      "
    >
      <TabList>
        <Tab
          value="planned"
        >
          {{
            t(
              'workload.tabs.planned',
            )
          }}
        </Tab>

        <Tab
          value="distribution"
        >
          {{
            t(
              'workloadDistribution.title',
            )
          }}
        </Tab>
      </TabList>

      <TabPanels>
        <TabPanel
          value="planned"
        >
          <PlannedWorkloadView
            v-if="
              activeTab ===
              'planned'
            "
          />
        </TabPanel>

        <TabPanel
          value="distribution"
        >
          <WorkloadDistributionView
            v-if="
              activeTab ===
              'distribution'
            "
          />
        </TabPanel>
      </TabPanels>
    </Tabs>
  </div>
</template>

<style scoped>
.workload-view {
  display: grid;
  gap: 1rem;
  min-width: 0;
}

:deep(.p-tabs) {
  min-width: 0;
}

:deep(.p-tabpanels) {
  padding:
    1rem
    0
    0;
}

:deep(.p-tabpanel) {
  min-width: 0;
}
</style>
