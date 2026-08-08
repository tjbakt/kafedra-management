<script setup lang="ts">
import Button from 'primevue/button'
import Select from 'primevue/select'
import Tag from 'primevue/tag'

import {
  computed,
  onMounted,
  ref,
} from 'vue'

import { useI18n } from 'vue-i18n'

import BaseCard from '@/components/base/BaseCard.vue'
import BaseDataTable from '@/components/base/BaseDataTable.vue'
import BasePageHeader from '@/components/base/BasePageHeader.vue'
import BaseToolbar from '@/components/base/BaseToolbar.vue'

import StaffMemberDetailsDialog from '@/modules/staff/components/StaffMemberDetailsDialog.vue'
import StaffMemberFormDialog from '@/modules/staff/components/StaffMemberFormDialog.vue'

import {
  getAcademicDegrees,
  getAcademicTitles,
  staffMembersApi,
} from '@/modules/staff/api'

import type {
  AcademicDegreeOption,
  AcademicTitleOption,
  SelectOption,
  StaffMember,
  StaffMemberPayload,
} from '@/modules/staff/types'

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

import {
  useLocaleStore,
} from '@/stores/locale'

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

const localeStore =
  useLocaleStore()

const toast =
  useAppToast()

const {
  confirmDelete,
} = useAppConfirm()

const {
  can,
} = usePermissions()

const selectedStaffMember =
  ref<StaffMember | null>(null)

const formVisible =
  ref(false)

const detailsVisible =
  ref(false)

const saving =
  ref(false)

const lookupsLoading =
  ref(false)

const academicDegrees =
  ref<AcademicDegreeOption[]>([])

const academicTitles =
  ref<AcademicTitleOption[]>([])

const selectedDegree =
  ref<number | null>(null)

const selectedTitle =
  ref<number | null>(null)

const selectedActive =
  ref<boolean | null>(null)

const fieldErrors =
  ref<FieldErrors>({})

const nonFieldErrors =
  ref<string[]>([])

const generalFormError =
  ref('')

const canCreate = computed(
  () =>
    can(
      'staff.add_staffmember',
    ),
)

const canEdit = computed(
  () =>
    can(
      'staff.change_staffmember',
    ),
)

const canDelete = computed(
  () =>
    can(
      'staff.delete_staffmember',
    ),
)

function localizedName(
  ru: string | null | undefined,
  uz: string | null | undefined,
): string {
  if (localeStore.locale === 'uz') {
    return (
      uz?.trim() ||
      ru?.trim() ||
      '—'
    )
  }

  return (
    ru?.trim() ||
    uz?.trim() ||
    '—'
  )
}

const degreeFilterOptions =
  computed<SelectOption[]>(() => [
    {
      id: null,
      label:
        t(
          'staff.allDegrees',
        ),
    },

    ...academicDegrees.value.map(
      (item) => ({
        id: item.id,

        label:
          localizedName(
            item.name_ru,
            item.name_uz,
          ),
      }),
    ),
  ])

const titleFilterOptions =
  computed<SelectOption[]>(() => [
    {
      id: null,
      label:
        t(
          'staff.allTitles',
        ),
    },

    ...academicTitles.value.map(
      (item) => ({
        id: item.id,

        label:
          localizedName(
            item.name_ru,
            item.name_uz,
          ),
      }),
    ),
  ])

const statusOptions =
  computed(() => [
    {
      label:
        t(
          'staff.allStatuses',
        ),
      value: null,
    },

    {
      label:
        t('staff.working'),
      value: true,
    },

    {
      label:
        t(
          'staff.notWorking',
        ),
      value: false,
    },
  ])

const columns =
  computed<
    CrudColumn<StaffMember>[]
  >(() => [
    {
      field:
        'personnel_number',

      header:
        t(
          'staff.fields.personnelNumber',
        ),

      sortable: true,

      minWidth: '9rem',
    },

    {
      field:
        'full_name',

      header:
        t(
          'staff.fields.fullName',
        ),

      sortable: true,

      sortField: 'last_name',

      minWidth: '17rem',
    },

    {
      field:
        'academic_degree_name',

      header:
        t(
          'staff.fields.academicDegree',
        ),

      bodySlot: 'degree',

      minWidth: '12rem',
    },

    {
      field:
        'academic_title_name',

      header:
        t(
          'staff.fields.academicTitle',
        ),

      bodySlot: 'title',

      minWidth: '12rem',
    },

    {
      field: 'phone',

      header:
        t(
          'staff.fields.phone',
        ),

      minWidth: '10rem',
    },

    {
      field: 'is_active',

      header:
        t(
          'staff.fields.status',
        ),

      bodySlot: 'status',

      width: '8rem',

      align: 'center',
    },
  ])

const {
  items,
  totalRecords,
  loading,
  error,

  query,
  searchInput,
  first,

  load,
  refresh,
  reset,

  handlePage,
  handleSort,

  setFilter,
  clearFilters,
} = useCrudList<StaffMember>(
  (params) =>
    staffMembersApi.list(
      params,
    ),

  {
    initialPageSize: 20,

    initialOrdering:
      'last_name,first_name',
  },
)

function clearFormErrors(): void {
  fieldErrors.value = {}

  nonFieldErrors.value = []

  generalFormError.value = ''
}

async function loadLookups(): Promise<void> {
  lookupsLoading.value = true

  try {
    const [
      degreesResponse,
      titlesResponse,
    ] = await Promise.all([
      getAcademicDegrees(),
      getAcademicTitles(),
    ])

    academicDegrees.value =
      degreesResponse.results

    academicTitles.value =
      titlesResponse.results
  } catch (lookupError) {
    const normalized =
      normalizeApiError(
        lookupError,
        t('crud.loadError'),
      )

    toast.error(
      t('common.error'),
      normalized.message,
    )
  } finally {
    lookupsLoading.value = false
  }
}

function openCreate(): void {
  selectedStaffMember.value =
    null

  clearFormErrors()

  formVisible.value = true
}

function openView(
  member: StaffMember,
): void {
  selectedStaffMember.value =
    member

  detailsVisible.value = true
}

function openEdit(
  member: StaffMember,
): void {
  selectedStaffMember.value =
    member

  clearFormErrors()

  formVisible.value = true
}

async function saveStaffMember(
  payload: StaffMemberPayload,
): Promise<void> {
  saving.value = true

  clearFormErrors()

  try {
    if (
      selectedStaffMember.value
    ) {
      await staffMembersApi.update(
        selectedStaffMember.value.id,
        payload,
      )

      toast.success(
        t('common.success'),
        t('crud.updated'),
      )
    } else {
      await staffMembersApi.create(
        payload,
      )

      toast.success(
        t('common.success'),
        t('crud.created'),
      )
    }

    formVisible.value = false

    selectedStaffMember.value =
      null

    await refresh()
  } catch (saveError) {
    const normalized =
      normalizeApiError(
        saveError,
        t('crud.saveError'),
      )

    fieldErrors.value =
      normalized.fieldErrors

    nonFieldErrors.value =
      normalized.nonFieldErrors

    generalFormError.value =
      normalized.message
  } finally {
    saving.value = false
  }
}

function archiveStaffMember(
  member: StaffMember,
): void {
  confirmDelete({
    header:
      t(
        'staff.archiveTitle',
      ),

    message:
      t(
        'staff.archiveConfirm',
        {
          name:
            member.full_name,
        },
      ),

    accept: async () => {
      try {
        await staffMembersApi.remove(
          member.id,
        )

        toast.success(
          t('common.success'),
          t('staff.archived'),
        )

        await refresh()
      } catch (archiveError) {
        const normalized =
          normalizeApiError(
            archiveError,
            t(
              'crud.deleteError',
            ),
          )

        toast.error(
          t('common.error'),
          normalized.message,
        )
      }
    },
  })
}

async function applyDegreeFilter(): Promise<void> {
  setFilter(
    'academic_degree',
    selectedDegree.value,
  )

  await load()
}

async function applyTitleFilter(): Promise<void> {
  setFilter(
    'academic_title',
    selectedTitle.value,
  )

  await load()
}

async function applyStatusFilter(): Promise<void> {
  setFilter(
    'is_active',
    selectedActive.value,
  )

  await load()
}

async function resetFilters(): Promise<void> {
  selectedDegree.value = null
  selectedTitle.value = null
  selectedActive.value = null

  clearFilters()

  await reset()
}

onMounted(async () => {
  await Promise.all([
    load(),
    loadLookups(),
  ])
})
</script>

<template>
  <div class="staff-page">
    <BasePageHeader
      :title="t('staff.title')"
      :description="
        t('staff.description')
      "
      icon="pi pi-users"
    >
      <template #actions>
        <Button
          v-if="canCreate"
          :label="
            t('staff.create')
          "
          icon="pi pi-plus"
          @click="openCreate"
        />
      </template>
    </BasePageHeader>

    <BaseToolbar
      v-model:search="
        searchInput
      "
      :show-create="false"
      :show-reset="true"
      :loading="
        loading ||
        lookupsLoading
      "
      :search-placeholder="
        t(
          'staff.searchPlaceholder',
        )
      "
      @refresh="refresh"
      @reset="
        resetFilters
      "
    >
      <template #center>
        <Select
          v-model="
            selectedDegree
          "
          :options="
            degreeFilterOptions
          "
          option-label="label"
          option-value="id"
          class="staff-filter"
          filter
          @change="
            applyDegreeFilter
          "
        />

        <Select
          v-model="
            selectedTitle
          "
          :options="
            titleFilterOptions
          "
          option-label="label"
          option-value="id"
          class="staff-filter"
          filter
          @change="
            applyTitleFilter
          "
        />

        <Select
          v-model="
            selectedActive
          "
          :options="
            statusOptions
          "
          option-label="label"
          option-value="value"
          class="
            staff-filter
            staff-filter--status
          "
          @change="
            applyStatusFilter
          "
        />
      </template>
    </BaseToolbar>

    <BaseCard
      :padding="false"
    >
      <BaseDataTable
        :value="items"
        :columns="columns"
        :loading="loading"
        :error="error"
        :first="first"
        :rows="
          query.pageSize
        "
        :total-records="
          totalRecords
        "
        show-row-actions
        @page="
          handlePage
        "
        @sort="
          handleSort
        "
        @retry="refresh"
        @row-click="
          openView
        "
      >
        <template
          #degree="{ row }"
        >
          {{
            row.academic_degree_name ||
            '—'
          }}
        </template>

        <template
          #title="{ row }"
        >
          {{
            row.academic_title_name ||
            '—'
          }}
        </template>

        <template
          #status="{ row }"
        >
          <Tag
            :value="
              row.is_active
                ? t(
                    'staff.working',
                  )
                : t(
                    'staff.notWorking',
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
            v-tooltip.bottom="
              t('common.view')
            "
            icon="pi pi-eye"
            severity="secondary"
            text
            rounded
            @click.stop="
              openView(row)
            "
          />

          <Button
            v-if="canEdit"
            v-tooltip.bottom="
              t('common.edit')
            "
            icon="pi pi-pencil"
            text
            rounded
            @click.stop="
              openEdit(row)
            "
          />

          <Button
            v-if="canDelete"
            v-tooltip.bottom="
              t('staff.archive')
            "
            icon="pi pi-box"
            severity="danger"
            text
            rounded
            @click.stop="
              archiveStaffMember(
                row,
              )
            "
          />
        </template>

        <template
          #emptyActions
        >
          <Button
            v-if="canCreate"
            :label="
              t('staff.create')
            "
            icon="pi pi-plus"
            @click="openCreate"
          />
        </template>
      </BaseDataTable>
    </BaseCard>

    <StaffMemberFormDialog
      v-model="formVisible"
      :staff-member="
        selectedStaffMember
      "
      :academic-degrees="
        academicDegrees
      "
      :academic-titles="
        academicTitles
      "
      :loading="saving"
      :field-errors="
        fieldErrors
      "
      :non-field-errors="
        nonFieldErrors
      "
      :general-error="
        generalFormError
      "
      @submit="
        saveStaffMember
      "
    />

    <StaffMemberDetailsDialog
      v-model="
        detailsVisible
      "
      :staff-member="
        selectedStaffMember
      "
    />
  </div>
</template>

<style scoped>
.staff-page {
  display: grid;
  gap: 1rem;
}

.staff-filter {
  width: 14rem;
}

.staff-filter--status {
  width: 11rem;
}

@media (max-width: 991px) {
  .staff-filter,
  .staff-filter--status {
    width: 100%;
  }
}
</style>
