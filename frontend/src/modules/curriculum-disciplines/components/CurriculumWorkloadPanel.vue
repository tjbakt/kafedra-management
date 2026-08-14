<script setup lang="ts">
import Button from 'primevue/button'
import Message from 'primevue/message'
import Tag from 'primevue/tag'

import {
  computed,
  onMounted,
  ref,
  watch,
} from 'vue'

import {
  useI18n,
} from 'vue-i18n'

import CurriculumWorkloadFormDialog
  from './CurriculumWorkloadFormDialog.vue'

import {
  curriculumWorkloadsApi,
  getCurriculumWorkloads,
  getWorkloadTypes,
} from '@/modules/curriculum-disciplines/workload-api'

import type {
  CurriculumDiscipline,
} from '@/modules/curriculum-disciplines/types'

import type {
  CurriculumWorkload,
  CurriculumWorkloadPayload,
  WorkloadType,
} from '@/modules/curriculum-disciplines/workload-types'

import {
  normalizeApiError,
} from '@/utils/api-errors'

import {
  useAppConfirm,
} from '@/composables/useAppConfirm'

import {
  useAppToast,
} from '@/composables/useAppToast'

const props =
  defineProps<{
    discipline:
      CurriculumDiscipline
  }>()

const emit =
  defineEmits<{
    changed: []
  }>()

const { t } =
  useI18n()

const toast =
  useAppToast()

const {
  confirmDelete,
} = useAppConfirm()

const items =
  ref<CurriculumWorkload[]>([])

const workloadTypes =
  ref<WorkloadType[]>([])

const loading =
  ref(false)

const saving =
  ref(false)

const formVisible =
  ref(false)

const selectedRecord =
  ref<CurriculumWorkload | null>(
    null,
  )

const fieldErrors =
  ref<Record<string, string[]>>(
    {},
  )

const nonFieldErrors =
  ref<string[]>([])

const generalError =
  ref('')

const error =
  ref('')

const totalHours =
  computed(() =>
    items.value
      .filter(
        (item) =>
          item.is_active &&
          !item.is_archived,
      )
      .reduce(
        (
          total,
          item,
        ) =>
          total +
          Number(
            item.base_hours,
          ),
        0,
      ),
  )

function clearFormErrors(): void {
  fieldErrors.value =
    {}

  nonFieldErrors.value =
    []

  generalError.value =
    ''
}

function localizedWorkloadName(
  item: CurriculumWorkload,
): string {
  const workloadType =
    workloadTypes.value.find(
      (type) =>
        type.id ===
        item.workload_type,
    )

  if (!workloadType) {
    return (
      item.workload_type_name ||
      '—'
    )
  }

  return (
    workloadType.display_name ||
    workloadType.name_ru ||
    workloadType.name_uz ||
    item.workload_type_name ||
    '—'
  )
}

function calculationModeLabel(
  mode:
    CurriculumWorkload['calculation_mode'],
): string {
  const keyMap = {
    fixed:
      'fixed',

    per_group:
      'perGroup',

    per_subgroup:
      'perSubgroup',

    per_student:
      'perStudent',
  } as const

  return t(
    `curriculumWorkloads.calculationModes.${keyMap[mode]}`,
  )
}

async function load(): Promise<void> {
  loading.value =
    true

  error.value =
    ''

  try {
    const [
      workloadResponse,
      workloadTypeResponse,
    ] =
      await Promise.all([
        getCurriculumWorkloads(
          props.discipline.id,
        ),

        getWorkloadTypes(),
      ])

    items.value =
      workloadResponse.results

    workloadTypes.value =
      workloadTypeResponse.results
  } catch (loadError) {
    const normalized =
      normalizeApiError(
        loadError,
        t(
          'curriculumWorkloads.loadError',
        ),
      )

    error.value =
      normalized.message

    toast.error(
      t('common.error'),
      normalized.message,
    )
  } finally {
    loading.value =
      false
  }
}

function openCreate(): void {
  selectedRecord.value =
    null

  clearFormErrors()

  formVisible.value =
    true
}

function openEdit(
  item: CurriculumWorkload,
): void {
  selectedRecord.value =
    item

  clearFormErrors()

  formVisible.value =
    true
}

async function save(
  payload:
    CurriculumWorkloadPayload,
): Promise<void> {
  saving.value =
    true

  clearFormErrors()

  try {
    if (
      selectedRecord.value
    ) {
      await curriculumWorkloadsApi
        .update(
          selectedRecord.value.id,
          payload,
        )

      toast.success(
        t('common.success'),
        t('crud.updated'),
      )
    } else {
      await curriculumWorkloadsApi
        .create(payload)

      toast.success(
        t('common.success'),
        t('crud.created'),
      )
    }

    formVisible.value =
      false

    selectedRecord.value =
      null

    await load()

    emit('changed')
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

    generalError.value =
      normalized.message
  } finally {
    saving.value =
      false
  }
}

function archive(
  item: CurriculumWorkload,
): void {
  confirmDelete({
    header:
      t(
        'curriculumWorkloads.archiveTitle',
      ),

    message:
      t(
        'curriculumWorkloads.archiveConfirm',
        {
          workload:
            localizedWorkloadName(
              item,
            ),
        },
      ),

    accept:
      async () => {
        try {
          await curriculumWorkloadsApi
            .remove(item.id)

          toast.success(
            t('common.success'),

            t(
              'curriculumWorkloads.archived',
            ),
          )

          await load()

          emit('changed')
        } catch (
          archiveError
        ) {
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

watch(
  () => props.discipline.id,
  async (
    currentId,
    previousId,
  ) => {
    if (
      currentId ===
      previousId
    ) {
      return
    }

    await load()
  },
)

onMounted(load)
</script>

<template>
  <section
    class="
      curriculum-workload-panel
    "
  >
    <header
      class="
        curriculum-workload-panel__header
      "
    >
      <div>
        <h4>
          {{
            discipline.discipline_code
          }}
          —
          {{
            discipline.discipline_name
          }}
        </h4>

        <p>
          {{
            t(
              'curriculumWorkloads.disciplineInfo',
              {
                semester:
                  discipline.semester_number,

                department:
                  discipline.teaching_department_name,
              },
            )
          }}
        </p>
      </div>

      <Button
        :label="
          t(
            'curriculumWorkloads.create',
          )
        "
        icon="pi pi-plus"
        size="small"
        @click="openCreate"
      />
    </header>

    <Message
      v-if="error"
      severity="error"
      :closable="false"
    >
      {{ error }}
    </Message>

    <div
      v-if="loading"
      class="
        curriculum-workload-panel__state
      "
    >
      <i
        class="
          pi pi-spin
          pi-spinner
        "
      />

      <span>
        {{
          t(
            'common.loading',
          )
        }}
      </span>
    </div>

    <div
      v-else-if="
        items.length === 0
      "
      class="
        curriculum-workload-panel__state
      "
    >
      <i
        class="
          pi pi-inbox
        "
      />

      <span>
        {{
          t(
            'curriculumWorkloads.empty',
          )
        }}
      </span>
    </div>

    <div
      v-else
      class="
        curriculum-workload-list
      "
    >
      <article
        v-for="
          item in items
        "
        :key="item.id"
        class="
          curriculum-workload-item
        "
      >
        <div
          class="
            curriculum-workload-item__main
          "
        >
          <strong>
            {{
              localizedWorkloadName(
                item,
              )
            }}
          </strong>

          <small>
            {{
              calculationModeLabel(
                item.calculation_mode,
              )
            }}
          </small>
        </div>

        <div
          class="
            curriculum-workload-item__hours
          "
        >
          <span>
            {{
              t(
                'curriculumWorkloads.fields.baseHours',
              )
            }}
          </span>

          <strong>
            {{
              Number(
                item.base_hours,
              ).toFixed(2)
            }}
          </strong>
        </div>

        <div
          v-if="
            item.students_per_unit
          "
          class="
            curriculum-workload-item__students
          "
        >
          <span>
            {{
              t(
                'curriculumWorkloads.fields.studentsPerUnitShort',
              )
            }}
          </span>

          <strong>
            {{
              item.students_per_unit
            }}
          </strong>
        </div>

        <Tag
          :value="
            item.is_active
              ? t(
                  'curriculumWorkloads.active',
                )
              : t(
                  'curriculumWorkloads.inactive',
                )
          "
          :severity="
            item.is_active
              ? 'success'
              : 'secondary'
          "
        />

        <div
          class="
            curriculum-workload-item__actions
          "
        >
          <Button
            v-tooltip.bottom="
              t('common.edit')
            "
            icon="pi pi-pencil"
            text
            rounded
            @click="
              openEdit(item)
            "
          />

          <Button
            v-tooltip.bottom="
              t(
                'curriculumWorkloads.archive',
              )
            "
            icon="pi pi-box"
            text
            rounded
            severity="danger"
            @click="
              archive(item)
            "
          />
        </div>

        <p
          v-if="item.notes"
          class="
            curriculum-workload-item__notes
          "
        >
          {{ item.notes }}
        </p>
      </article>
    </div>

    <footer
      class="
        curriculum-workload-panel__footer
      "
    >
      <span>
        {{
          t(
            'curriculumWorkloads.total',
          )
        }}
      </span>

      <strong>
        {{
          totalHours.toFixed(
            2,
          )
        }}
      </strong>
    </footer>

    <CurriculumWorkloadFormDialog
      v-model="
        formVisible
      "
      :curriculum-discipline-id="
        discipline.id
      "
      :record="
        selectedRecord
      "
      :workload-types="
        workloadTypes
      "
      :loading="saving"
      :field-errors="
        fieldErrors
      "
      :non-field-errors="
        nonFieldErrors
      "
      :general-error="
        generalError
      "
      @submit="save"
    />
  </section>
</template>

<style scoped>
.curriculum-workload-panel {
  display: grid;
  gap: 1rem;
}

.curriculum-workload-panel__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.curriculum-workload-panel__header h4 {
  margin: 0;
  font-size: 1rem;
}

.curriculum-workload-panel__header p {
  margin: 0.25rem 0 0;

  color:
    var(--app-text-muted);

  font-size: 0.75rem;
}

.curriculum-workload-panel__state {
  display: flex;
  align-items: center;
  justify-content: center;

  min-height: 8rem;

  gap: 0.5rem;

  color:
    var(--app-text-muted);
}

.curriculum-workload-list {
  display: grid;
  gap: 0.6rem;
}

.curriculum-workload-item {
  display: grid;

  grid-template-columns:
    minmax(
      12rem,
      1fr
    )
    7rem
    7rem
    auto
    auto;

  align-items: center;

  gap: 0.75rem;

  padding:
    0.8rem 0.9rem;

  border:
    1px solid
    var(--app-border-color);

  border-radius:
    var(--app-radius-md);

  background:
    var(--app-surface);
}

.curriculum-workload-item__main {
  display: grid;
  gap: 0.15rem;
}

.curriculum-workload-item__main strong {
  font-size: 0.82rem;
}

.curriculum-workload-item__main small {
  color:
    var(--app-text-muted);

  font-size: 0.7rem;
}

.curriculum-workload-item__hours,
.curriculum-workload-item__students {
  display: grid;
  gap: 0.1rem;
}

.curriculum-workload-item__hours span,
.curriculum-workload-item__students span {
  color:
    var(--app-text-muted);

  font-size: 0.65rem;
}

.curriculum-workload-item__hours strong,
.curriculum-workload-item__students strong {
  font-size: 0.8rem;
  font-variant-numeric:
    tabular-nums;
}

.curriculum-workload-item__actions {
  display: flex;
  gap: 0.15rem;
}

.curriculum-workload-item__notes {
  grid-column:
    1 / -1;

  margin: 0;

  color:
    var(--app-text-muted);

  font-size: 0.72rem;

  line-height: 1.5;
}

.curriculum-workload-panel__footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;

  gap: 1rem;

  padding-top:
    0.8rem;

  border-top:
    1px solid
    var(--app-border-color);
}

.curriculum-workload-panel__footer span {
  color:
    var(--app-text-muted);

  font-size: 0.78rem;
}

.curriculum-workload-panel__footer strong {
  font-size: 1rem;

  font-variant-numeric:
    tabular-nums;
}

@media (
  max-width: 800px
) {
  .curriculum-workload-panel__header {
    align-items: stretch;
    flex-direction: column;
  }

  .curriculum-workload-item {
    grid-template-columns:
      1fr auto;
  }

  .curriculum-workload-item__notes {
    grid-column:
      1 / -1;
  }
}
</style>
