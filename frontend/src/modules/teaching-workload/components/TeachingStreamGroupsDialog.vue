<script setup lang="ts">
import Button from 'primevue/button'
import Checkbox from 'primevue/checkbox'
import Message from 'primevue/message'
import Select from 'primevue/select'
import Tag from 'primevue/tag'

import {
  computed,
  ref,
  watch,
} from 'vue'

import {
  useI18n,
} from 'vue-i18n'

import BaseDialog from '@/components/base/BaseDialog.vue'

import {
  teachingStreamGroupsApi,
} from '@/modules/teaching-workload/api'

import type {
  GroupSemester,
  TeachingStream,
  TeachingStreamGroup,
} from '@/modules/teaching-workload/types'

import {
  normalizeApiError,
} from '@/utils/api-errors'

import {
  useAppConfirm,
} from '@/composables/useAppConfirm'

import {
  useAppToast,
} from '@/composables/useAppToast'

const visible =
  defineModel<boolean>({
    default: false,
  })

const props =
  defineProps<{
    stream: TeachingStream | null

    groupSemesters:
      GroupSemester[]
  }>()

const emit =
  defineEmits<{
    changed: []
  }>()

const { t } = useI18n()

const toast =
  useAppToast()

const {
  confirmDelete,
} = useAppConfirm()

const selectedGroupSemester =
  ref<number | null>(null)

const active =
  ref(true)

const saving =
  ref(false)

const error =
  ref('')

const localGroups =
  ref<TeachingStreamGroup[]>([])

const compatibleGroupOptions =
  computed(() => {
    const stream =
      props.stream

    if (!stream) {
      return []
    }

    const existingIds =
      new Set(
        localGroups.value
          .filter(
            (item) =>
              !item.is_archived,
          )
          .map(
            (item) =>
              item.group_semester,
          ),
      )

    return props.groupSemesters
      .filter(
        (semester) =>
          semester.is_active &&
          !semester.is_archived &&

          semester.academic_year ===
            stream.academic_year &&

          semester.academic_semester ===
            stream.academic_semester &&

          semester.semester_number ===
            stream.semester_number &&

          semester.curriculum ===
            stream.curriculum &&

          !existingIds.has(
            semester.id,
          ),
      )
      .map(
        (semester) => ({
          value:
            semester.id,

          label:
            semester.student_group_code,

          description:
            t(
              'teachingWorkload.streamGroups.groupDescription',
              {
                students:
                  semester.students_count,

                subgroups:
                  semester.subgroup_count,
              },
            ),
        }),
      )
  })


async function loadGroups(): Promise<void> {
  if (!props.stream) {
    localGroups.value = []

    return
  }

  try {
    const response =
      await teachingStreamGroupsApi.list({
        teaching_stream:
          props.stream.id,

        page_size: 500,
      })

    localGroups.value =
      response.results
  } catch (loadError) {
    error.value =
      normalizeApiError(
        loadError,
        t('crud.loadError'),
      ).message
  }
}

async function addGroup(): Promise<void> {
  if (
    !props.stream ||
    !selectedGroupSemester.value
  ) {
    return
  }

  saving.value = true

  error.value = ''

  try {
    await teachingStreamGroupsApi.create({
      teaching_stream:
        props.stream.id,

      group_semester:
        selectedGroupSemester.value,

      is_active:
        active.value,

      notes: '',
    })

    selectedGroupSemester.value =
      null

    await loadGroups()

    emit('changed')

    toast.success(
      t('common.success'),

      t(
        'teachingWorkload.streamGroups.added',
      ),
    )
  } catch (saveError) {
    const normalized =
      normalizeApiError(
        saveError,
        t('crud.saveError'),
      )

    error.value =
      normalized.message

    toast.error(
      t('common.error'),
      normalized.message,
    )
  } finally {
    saving.value = false
  }
}

function archiveGroup(
  item: TeachingStreamGroup,
): void {
  confirmDelete({
    header:
      t(
        'teachingWorkload.streamGroups.archiveTitle',
      ),

    message:
      t(
        'teachingWorkload.streamGroups.archiveConfirm',
        {
          group:
            item.student_group_code,
        },
      ),

    accept:
      async () => {
        try {
          await teachingStreamGroupsApi.remove(
            item.id,
          )

          await loadGroups()

          emit('changed')

          toast.success(
            t('common.success'),

            t(
              'teachingWorkload.streamGroups.archived',
            ),
          )
        } catch (
          archiveError
        ) {
          toast.error(
            t('common.error'),

            normalizeApiError(
              archiveError,
            ).message,
          )
        }
      },
  })
}

watch(
  () => visible.value,
  async (isVisible) => {
    if (!isVisible) {
      return
    }

    selectedGroupSemester.value =
      null

    active.value = true

    error.value = ''

    await loadGroups()
  },
)

watch(
  () => props.stream?.id,
  async () => {
    if (visible.value) {
      await loadGroups()
    }
  },
)
</script>

<template>
  <BaseDialog
    v-model="visible"
    :title="
      stream
        ? `${t(
            'teachingWorkload.streamGroups.title',
          )}: ${stream.code}`
        : t(
            'teachingWorkload.streamGroups.title',
          )
    "
    width="62rem"
  >
    <div
      v-if="stream"
      class="
        stream-groups-dialog
      "
    >
      <div
        class="
          stream-groups-dialog__summary
        "
      >
        <div>
          <span>
            {{
              t(
                'teachingWorkload.streamGroups.groups',
              )
            }}
          </span>

          <strong>
            {{
              localGroups.filter(
                (item) =>
                  item.is_active &&
                  !item.is_archived,
              ).length
            }}
          </strong>
        </div>

        <div>
          <span>
            {{
              t(
                'teachingWorkload.streamGroups.students',
              )
            }}
          </span>

          <strong>
            {{
              localGroups
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
                    item.students_count,
                  0,
                )
            }}
          </strong>
        </div>

        <div>
          <span>
            {{
              t(
                'teachingWorkload.streamGroups.subgroups',
              )
            }}
          </span>

          <strong>
            {{
              localGroups
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
                    item.subgroup_count,
                  0,
                )
            }}
          </strong>
        </div>
      </div>

      <Message
        v-if="error"
        severity="error"
        :closable="false"
      >
        {{ error }}
      </Message>

      <div
        class="
          stream-groups-dialog__add
        "
      >
        <Select
          v-model="
            selectedGroupSemester
          "
          :options="compatibleGroupOptions"
          option-label="label"
          option-value="value"
          filter
          class="w-full"
          :placeholder="
            t(
              'teachingWorkload.streamGroups.selectGroup',
            )
          "
          :disabled="saving"
        >
          <template
            #option="{ option }"
          >
            <div
              class="group-option"
            >
              <strong>
                {{ option.label }}
              </strong>

              <small>
                {{
                  option.description
                }}
              </small>
            </div>
          </template>
        </Select>

        <label>
          <Checkbox
            v-model="active"
            binary
            :disabled="saving"
          />

          <span>
            {{
              t(
                'teachingWorkload.common.active',
              )
            }}
          </span>
        </label>

        <Button
          :label="
            t(
              'teachingWorkload.streamGroups.add',
            )
          "
          icon="pi pi-plus"
          :loading="saving"
          :disabled="
            !selectedGroupSemester
          "
          @click="addGroup"
        />
      </div>

      <div
        v-if="
          localGroups.length
        "
        class="
          stream-groups-dialog__list
        "
      >
        <article
          v-for="
            item in localGroups
          "
          :key="item.id"
          class="
            stream-group-item
          "
        >
          <div>
            <strong>
              {{
                item.student_group_code
              }}
            </strong>

            <small>
              {{
                t(
                  'teachingWorkload.streamGroups.groupDescription',
                  {
                    students:
                      item.students_count,

                    subgroups:
                      item.subgroup_count,
                  },
                )
              }}
            </small>
          </div>

          <Tag
            :value="
              item.is_active
                ? t(
                    'teachingWorkload.common.active',
                  )
                : t(
                    'teachingWorkload.common.inactive',
                  )
            "
            :severity="
              item.is_active
                ? 'success'
                : 'secondary'
            "
          />

          <Button
            v-tooltip.bottom="
              t(
                'teachingWorkload.streamGroups.archive',
              )
            "
            icon="pi pi-box"
            severity="danger"
            text
            rounded
            @click="
              archiveGroup(item)
            "
          />
        </article>
      </div>

      <div
        v-else
        class="
          stream-groups-dialog__empty
        "
      >
        {{
          t(
            'teachingWorkload.streamGroups.empty',
          )
        }}
      </div>
    </div>
  </BaseDialog>
</template>

<style scoped>
.stream-groups-dialog {
  display: grid;
  gap: 1rem;
}

.stream-groups-dialog__summary {
  display: grid;
  grid-template-columns:
    repeat(
      3,
      minmax(0, 1fr)
    );
  gap: 1rem;
}

.stream-groups-dialog__summary > div {
  display: grid;
  gap: 0.2rem;

  padding: 0.8rem;

  border:
    1px solid
    var(--app-border-color);

  border-radius:
    var(--app-radius-md);
}

.stream-groups-dialog__summary span {
  color:
    var(--app-text-muted);

  font-size: 0.72rem;
}

.stream-groups-dialog__summary strong {
  font-size: 1.1rem;
}

.stream-groups-dialog__add {
  display: grid;

  grid-template-columns:
    minmax(15rem, 1fr)
    auto
    auto;

  align-items: center;

  gap: 0.75rem;
}

.stream-groups-dialog__add label {
  display: flex;
  align-items: center;
  gap: 0.4rem;

  font-size: 0.8rem;
}

.group-option {
  display: grid;
  gap: 0.15rem;
}

.group-option small {
  color:
    var(--app-text-muted);

  font-size: 0.7rem;
}

.stream-groups-dialog__list {
  display: grid;
  gap: 0.5rem;
}

.stream-group-item {
  display: grid;

  grid-template-columns:
    1fr auto auto;

  align-items: center;

  gap: 0.75rem;

  padding: 0.75rem;

  border:
    1px solid
    var(--app-border-color);

  border-radius:
    var(--app-radius-md);
}

.stream-group-item > div {
  display: grid;
  gap: 0.1rem;
}

.stream-group-item small {
  color:
    var(--app-text-muted);

  font-size: 0.7rem;
}

.stream-groups-dialog__empty {
  padding: 2rem;

  color:
    var(--app-text-muted);

  text-align: center;
}

@media (max-width: 700px) {
  .stream-groups-dialog__summary {
    grid-template-columns: 1fr;
  }

  .stream-groups-dialog__add {
    grid-template-columns: 1fr;
  }
}
</style>
