<script setup lang="ts">
import Button from 'primevue/button'
import Tag from 'primevue/tag'

import {
  computed,
  onMounted,
  ref,
} from 'vue'

import {
  useI18n,
} from 'vue-i18n'

import Tab from 'primevue/tab'
import TabList from 'primevue/tablist'
import TabPanel from 'primevue/tabpanel'
import TabPanels from 'primevue/tabpanels'
import Tabs from 'primevue/tabs'

import BaseCard from '@/components/base/BaseCard.vue'
import BaseDataTable from '@/components/base/BaseDataTable.vue'
import BasePageHeader from '@/components/base/BasePageHeader.vue'

import StaffPositionFormDialog
  from '@/modules/staff-references/components/StaffPositionFormDialog.vue'

import AcademicDegreeFormDialog
  from '@/modules/staff-references/components/AcademicDegreeFormDialog.vue'

import AcademicTitleFormDialog
  from '@/modules/staff-references/components/AcademicTitleFormDialog.vue'

import {
  staffPositionsApi,
  academicDegreesApi,
  academicTitlesApi,
} from '@/modules/staff-references/api'

import type {
  AcademicDegree,
  AcademicDegreePayload,
  AcademicTitle,
  AcademicTitlePayload,
  StaffPosition,
  StaffPositionPayload,
} from '@/modules/staff-references/types'

import {
  useCrudList,
} from '@/composables/useCrudList'

import {
  useAppConfirm,
} from '@/composables/useAppConfirm'

import {
  useAppToast,
} from '@/composables/useAppToast'

import {
  usePermissions,
} from '@/composables/usePermissions'

import type {
  CrudColumn,
} from '@/types/crud'

import type {
  FieldErrors,
} from '@/types/validation'

import {
  normalizeApiError,
} from '@/utils/api-errors'

const { t } = useI18n()

const toast = useAppToast()

const {
  confirmDelete,
} = useAppConfirm()

const {
  can,
} = usePermissions()

const activeTab =
  ref('positions')

const positionDialog =
  ref(false)

const degreeDialog =
  ref(false)

const titleDialog =
  ref(false)

const selectedPosition =
  ref<StaffPosition | null>(null)

const selectedDegree =
  ref<AcademicDegree | null>(null)

const selectedTitle =
  ref<AcademicTitle | null>(null)

const saving =
  ref(false)

const fieldErrors =
  ref<FieldErrors>({})

const nonFieldErrors =
  ref<string[]>([])

const generalError =
  ref('')

const canCreatePosition =
  computed(() =>
    can(
      'staff.add_staffposition',
    ),
  )

const canEditPosition =
  computed(() =>
    can(
      'staff.change_staffposition',
    ),
  )

const canDeletePosition =
  computed(() =>
    can(
      'staff.delete_staffposition',
    ),
  )

const canCreateDegree =
  computed(() =>
    can(
      'staff.add_academicdegree',
    ),
  )

const canEditDegree =
  computed(() =>
    can(
      'staff.change_academicdegree',
    ),
  )

const canDeleteDegree =
  computed(() =>
    can(
      'staff.delete_academicdegree',
    ),
  )

const canCreateTitle =
  computed(() =>
    can(
      'staff.add_academic_title',
    ),
  )

const canEditTitle =
  computed(() =>
    can(
      'staff.change_academic_title',
    ),
  )

const canDeleteTitle =
  computed(() =>
    can(
      'staff.delete_academic_title',
    ),
  )

const {
  items: positionItems,
  totalRecords: positionTotalRecords,
  loading: positionsLoading,
  error: positionsError,
  query: positionsQuery,
  first: positionsFirst,
  load: loadPositions,
  refresh: refreshPositions,
  handlePage: handlePositionsPage,
  handleSort: handlePositionsSort,
} = useCrudList<StaffPosition>(
  (params) => staffPositionsApi.list(params),
  {
    initialPageSize: 20,
    initialOrdering: 'sort_order,name_ru',
  },
)

const {
  items: degreeItems,
  totalRecords: degreeTotalRecords,
  loading: degreesLoading,
  error: degreesError,
  query: degreesQuery,
  first: degreesFirst,
  load: loadDegrees,
  refresh: refreshDegrees,
  handlePage: handleDegreesPage,
  handleSort: handleDegreesSort,
} = useCrudList<AcademicDegree>(
  (params) => academicDegreesApi.list(params),
  {
    initialPageSize: 20,
    initialOrdering: 'sort_order,name_ru',
  },
)

const {
  items: titleItems,
  totalRecords: titleTotalRecords,
  loading: titlesLoading,
  error: titlesError,
  query: titlesQuery,
  first: titlesFirst,
  load: loadTitles,
  refresh: refreshTitles,
  handlePage: handleTitlesPage,
  handleSort: handleTitlesSort,
} = useCrudList<AcademicTitle>(
  (params) => academicTitlesApi.list(params),
  {
    initialPageSize: 20,
    initialOrdering: 'sort_order,name_ru',
  },
)

const positionColumns =
  computed<
    CrudColumn<StaffPosition>[]
  >(() => [
    {
      field: 'code',
      header:
        t(
          'staffReferences.common.code',
        ),
      sortable: true,
      minWidth: '9rem',
    },
    {
      field: 'display_name',
      header:
        t(
          'staffReferences.common.name',
        ),
      sortable: true,
      minWidth: '18rem',
    },
    {
      field: 'category_name',
      header:
        t(
          'staffReferences.positions.category',
        ),
      minWidth: '18rem',
    },
    {
      field:
        'is_teaching_position',
      header:
        t(
          'staffReferences.positions.teachingPositionShort',
        ),
      bodySlot:
        'teaching',
      width: '10rem',
      align: 'center',
    },
    {
      field: 'is_active',
      header:
        t(
          'staffReferences.common.status',
        ),
      bodySlot:
        'status',
      width: '9rem',
      align: 'center',
    },
  ])

const degreeColumns =
  computed<
    CrudColumn<AcademicDegree>[]
  >(() => [
    {
      field: 'code',
      header:
        t(
          'staffReferences.common.code',
        ),
      sortable: true,
      minWidth: '9rem',
    },
    {
      field: 'display_name',
      header:
        t(
          'staffReferences.common.name',
        ),
      sortable: true,
      minWidth: '20rem',
    },
    {
      field: 'short_name_ru',
      header:
        t(
          'staffReferences.common.shortNameRu',
        ),
      minWidth: '12rem',
    },
    {
      field: 'is_active',
      header:
        t(
          'staffReferences.common.status',
        ),
      bodySlot:
        'status',
      width: '9rem',
      align: 'center',
    },
  ])

const titleColumns =
  computed<
    CrudColumn<AcademicTitle>[]
  >(() => [
    {
      field: 'code',
      header:
        t(
          'staffReferences.common.code',
        ),
      sortable: true,
      minWidth: '9rem',
    },
    {
      field: 'display_name',
      header:
        t(
          'staffReferences.common.name',
        ),
      sortable: true,
      minWidth: '20rem',
    },
    {
      field: 'short_name_ru',
      header:
        t(
          'staffReferences.common.shortNameRu',
        ),
      minWidth: '12rem',
    },
    {
      field: 'is_active',
      header:
        t(
          'staffReferences.common.status',
        ),
      bodySlot:
        'status',
      width: '9rem',
      align: 'center',
    },
  ])

function clearErrors(): void {
  fieldErrors.value = {}
  nonFieldErrors.value = []
  generalError.value = ''
}

function openCreatePosition(): void {
  selectedPosition.value = null
  clearErrors()
  positionDialog.value = true
}

function openEditPosition(
  record: StaffPosition,
): void {
  selectedPosition.value = record
  clearErrors()
  positionDialog.value = true
}

function openCreateDegree(): void {
  selectedDegree.value = null
  clearErrors()
  degreeDialog.value = true
}

function openEditDegree(
  record: AcademicDegree,
): void {
  selectedDegree.value = record
  clearErrors()
  degreeDialog.value = true
}

function openCreateTitle(): void {
  selectedTitle.value = null
  clearErrors()
  titleDialog.value = true
}

function openEditTitle(
  record: AcademicTitle,
): void {
  selectedTitle.value = record
  clearErrors()
  titleDialog.value = true
}

async function savePosition(
  payload: StaffPositionPayload,
): Promise<void> {
  saving.value = true
  clearErrors()

  try {
    if (selectedPosition.value) {
      await staffPositionsApi.update(
        selectedPosition.value.id,
        payload,
      )
    } else {
      await staffPositionsApi.create(
        payload,
      )
    }

    positionDialog.value = false

    toast.success(
      t('common.success'),
      t(
        selectedPosition.value
          ? 'crud.updated'
          : 'crud.created',
      ),
    )

    await refreshPositions()
  } catch (error) {
    const normalized =
      normalizeApiError(
        error,
        t('crud.saveError'),
      )

    fieldErrors.value =
      normalized.fieldErrors

    nonFieldErrors.value =
      normalized.nonFieldErrors

    generalError.value =
      normalized.message
  } finally {
    saving.value = false
  }
}

async function saveDegree(
  payload: AcademicDegreePayload,
): Promise<void> {
  saving.value = true
  clearErrors()

  try {
    if (selectedDegree.value) {
      await academicDegreesApi.update(
        selectedDegree.value.id,
        payload,
      )
    } else {
      await academicDegreesApi.create(
        payload,
      )
    }

    degreeDialog.value = false

    toast.success(
      t('common.success'),
      t(
        selectedDegree.value
          ? 'crud.updated'
          : 'crud.created',
      ),
    )

    await refreshDegrees()
  } catch (error) {
    const normalized =
      normalizeApiError(
        error,
        t('crud.saveError'),
      )

    fieldErrors.value =
      normalized.fieldErrors

    nonFieldErrors.value =
      normalized.nonFieldErrors

    generalError.value =
      normalized.message
  } finally {
    saving.value = false
  }
}

async function saveTitle(
  payload: AcademicTitlePayload,
): Promise<void> {
  saving.value = true
  clearErrors()

  try {
    if (selectedTitle.value) {
      await academicTitlesApi.update(
        selectedTitle.value.id,
        payload,
      )
    } else {
      await academicTitlesApi.create(
        payload,
      )
    }

    titleDialog.value = false

    toast.success(
      t('common.success'),
      t(
        selectedTitle.value
          ? 'crud.updated'
          : 'crud.created',
      ),
    )

    await refreshTitles()
  } catch (error) {
    const normalized =
      normalizeApiError(
        error,
        t('crud.saveError'),
      )

    fieldErrors.value =
      normalized.fieldErrors

    nonFieldErrors.value =
      normalized.nonFieldErrors

    generalError.value =
      normalized.message
  } finally {
    saving.value = false
  }
}

function archivePosition(
  record: StaffPosition,
): void {
  confirmDelete({
    header:
      t(
        'staffReferences.positions.archiveTitle',
      ),
    message:
      t(
        'staffReferences.positions.archiveConfirm',
        {
          name:
            record.display_name,
        },
      ),
    accept: async () => {
      try {
        await staffPositionsApi.remove(
          record.id,
        )

        toast.success(
          t('common.success'),
          t(
            'staffReferences.common.archived',
          ),
        )

        await refreshPositions()
      } catch (error) {
        const normalized =
          normalizeApiError(
            error,
            t('crud.deleteError'),
          )

        toast.error(
          t('common.error'),
          normalized.message,
        )
      }
    },
  })
}

function archiveDegree(
  record: AcademicDegree,
): void {
  confirmDelete({
    header:
      t(
        'staffReferences.degrees.archiveTitle',
      ),
    message:
      t(
        'staffReferences.degrees.archiveConfirm',
        {
          name:
            record.display_name,
        },
      ),
    accept: async () => {
      try {
        await academicDegreesApi.remove(
          record.id,
        )

        toast.success(
          t('common.success'),
          t(
            'staffReferences.common.archived',
          ),
        )

        await refreshDegrees()
      } catch (error) {
        const normalized =
          normalizeApiError(
            error,
            t('crud.deleteError'),
          )

        toast.error(
          t('common.error'),
          normalized.message,
        )
      }
    },
  })
}

function archiveTitle(
  record: AcademicTitle,
): void {
  confirmDelete({
    header:
      t(
        'staffReferences.titles.archiveTitle',
      ),
    message:
      t(
        'staffReferences.titles.archiveConfirm',
        {
          name:
            record.display_name,
        },
      ),
    accept: async () => {
      try {
        await academicTitlesApi.remove(
          record.id,
        )

        toast.success(
          t('common.success'),
          t(
            'staffReferences.common.archived',
          ),
        )

        await refreshTitles()
      } catch (error) {
        const normalized =
          normalizeApiError(
            error,
            t('crud.deleteError'),
          )

        toast.error(
          t('common.error'),
          normalized.message,
        )
      }
    },
  })
}

onMounted(async () => {
  await Promise.all([
    loadPositions(),
    loadDegrees(),
    loadTitles(),
  ])
})
</script>

<template>
  <div class="staff-references-page">
    <BasePageHeader
      :title="
        t(
          'staffReferences.title',
        )
      "
      :description="
        t(
          'staffReferences.description',
        )
      "
      icon="pi pi-id-card"
    />

    <Tabs
      v-model:value="activeTab"
    >
      <TabList>
        <Tab value="positions">
          <i class="pi pi-briefcase" />
          {{
            t(
              'staffReferences.tabs.positions',
            )
          }}
        </Tab>

        <Tab value="degrees">
          <i class="pi pi-graduation-cap" />
          {{
            t(
              'staffReferences.tabs.degrees',
            )
          }}
        </Tab>

        <Tab value="titles">
          <i class="pi pi-star" />
          {{
            t(
              'staffReferences.tabs.titles',
            )
          }}
        </Tab>
      </TabList>

      <TabPanels>
        <TabPanel value="positions">
          <BaseCard :padding="false">
            <div class="reference-toolbar">
              <Button
                v-if="
                  canCreatePosition
                "
                :label="
                  t(
                    'staffReferences.positions.create',
                  )
                "
                icon="pi pi-plus"
                @click="
                  openCreatePosition
                "
              />
            </div>

            <BaseDataTable
              :value="positionItems"
              :columns="positionColumns"
              :loading="positionsLoading"
              :error="positionsError"
              :first="positionsFirst"
              :rows="positionsQuery.pageSize"
              :total-records="positionTotalRecords"
              show-row-actions
              @page="handlePositionsPage"
              @sort="handlePositionsSort"
              @retry="refreshPositions"
            >
              <template #teaching="{ row }">
                <Tag
                  :value="
                    row.is_teaching_position
                      ? t(
                          'common.yes',
                        )
                      : t(
                          'common.no',
                        )
                  "
                  :severity="
                    row.is_teaching_position
                      ? 'success'
                      : 'secondary'
                  "
                />
              </template>

              <template #status="{ row }">
                <Tag
                  :value="
                    row.is_active
                      ? t(
                          'staffReferences.common.active',
                        )
                      : t(
                          'staffReferences.common.inactive',
                        )
                  "
                  :severity="
                    row.is_active
                      ? 'success'
                      : 'secondary'
                  "
                />
              </template>

              <template #actions="{ row }">
                <Button
                  v-if="canEditPosition"
                  icon="pi pi-pencil"
                  text
                  rounded
                  @click.stop="openEditPosition(row, )"
                />

                <Button
                  v-if="canDeletePosition"
                  icon="pi pi-box"
                  severity="danger"
                  text
                  rounded
                  @click.stop="archivePosition(row,)"
                />
              </template>
            </BaseDataTable>
          </BaseCard>
        </TabPanel>

        <TabPanel value="degrees">
          <BaseCard :padding="false">
            <div class="reference-toolbar">
              <Button
                v-if="canCreateDegree"
                :label="
                  t(
                    'staffReferences.degrees.create',
                  )
                "
                icon="pi pi-plus"
                @click="openCreateDegree"
              />
            </div>

            <BaseDataTable
              :value="degreeItems"
              :columns="degreeColumns"
              :loading="degreesLoading"
              :error="degreesError"
              :first="degreesFirst"
              :rows="degreesQuery.pageSize"
              :total-records="degreeTotalRecords"
              show-row-actions
              @page="handleDegreesPage"
              @sort="handleDegreesSort"
              @retry="refreshDegrees"
            >
              <template #status="{ row }">
                <Tag
                  :value="
                    row.is_active
                      ? t(
                          'staffReferences.common.active',
                        )
                      : t(
                          'staffReferences.common.inactive',
                        )
                  "
                  :severity="
                    row.is_active
                      ? 'success'
                      : 'secondary'
                  "
                />
              </template>

              <template #actions="{ row }">
                <Button
                  v-if="canEditDegree"
                  icon="pi pi-pencil"
                  text
                  rounded
                  @click.stop="
                    openEditDegree(
                      row,
                    )
                  "
                />

                <Button
                  v-if="canDeleteDegree"
                  icon="pi pi-box"
                  severity="danger"
                  text
                  rounded
                  @click.stop="
                    archiveDegree(
                      row,
                    )
                  "
                />
              </template>
            </BaseDataTable>
          </BaseCard>
        </TabPanel>

        <TabPanel value="titles">
          <BaseCard :padding="false">
            <div class="reference-toolbar">
              <Button
                v-if="canCreateTitle"
                :label="
                  t(
                    'staffReferences.titles.create',
                  )
                "
                icon="pi pi-plus"
                @click="openCreateTitle"
              />
            </div>

            <BaseDataTable
              :value="titleItems"
              :columns="titleColumns"
              :loading="titlesLoading"
              :error="titlesError"
              :first="titlesFirst"
              :rows="titlesQuery.pageSize"
              :total-records="titleTotalRecords"
              show-row-actions
              @page="handleTitlesPage"
              @sort="handleTitlesSort"
              @retry="refreshTitles"
            >
              <template #status="{ row }">
                <Tag
                  :value="
                    row.is_active
                      ? t(
                          'staffReferences.common.active',
                        )
                      : t(
                          'staffReferences.common.inactive',
                        )
                  "
                  :severity="
                    row.is_active
                      ? 'success'
                      : 'secondary'
                  "
                />
              </template>

              <template
                #actions="{ row }"
              >
                <Button
                  v-if="canEditTitle"
                  icon="pi pi-pencil"
                  text
                  rounded
                  @click.stop="
                    openEditTitle(
                      row,
                    )
                  "
                />

                <Button
                  v-if="canDeleteTitle"
                  icon="pi pi-box"
                  severity="danger"
                  text
                  rounded
                  @click.stop="
                    archiveTitle(
                      row,
                    )
                  "
                />
              </template>
            </BaseDataTable>
          </BaseCard>
        </TabPanel>
      </TabPanels>
    </Tabs>

    <StaffPositionFormDialog
      v-model="positionDialog"
      :record="selectedPosition"
      :loading="saving"
      :field-errors="fieldErrors"
      :non-field-errors="nonFieldErrors"
      :general-error="generalError"
      @submit="savePosition"
    />

    <AcademicDegreeFormDialog
      v-model="degreeDialog"
      :record="selectedDegree"
      :loading="saving"
      :field-errors="fieldErrors"
      :non-field-errors="nonFieldErrors"
      :general-error="generalError"
      @submit="saveDegree"
    />

    <AcademicTitleFormDialog
      v-model="titleDialog"
      :record="selectedTitle"
      :loading="saving"
      :field-errors="fieldErrors"
      :non-field-errors="nonFieldErrors"
      :general-error="generalError"
      @submit="saveTitle"
    />
  </div>
</template>

<style scoped>
.staff-references-page {
  display: grid;
  gap: 1rem;
}

.reference-toolbar {
  display: flex;
  justify-content: flex-end;
  padding: 1rem;
}

.staff-references-page :deep(.p-tablist) {
  overflow-x: auto;
}

.staff-references-page :deep(.p-tab) {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  white-space: nowrap;
}
</style>
