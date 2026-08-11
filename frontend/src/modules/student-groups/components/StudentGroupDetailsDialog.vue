<script setup lang="ts">
import Tag from 'primevue/tag'

import {
  computed,
} from 'vue'

import {
  useI18n,
} from 'vue-i18n'

import BaseDialog from '@/components/base/BaseDialog.vue'

import type {
  StudentGroup,
} from '@/modules/student-groups/types'

const visible =
  defineModel<boolean>({
    default: false,
  })

const props =
  defineProps<{
    studentGroup:
      StudentGroup | null
  }>()

const { t } = useI18n()

const dialogTitle = computed(
  () =>
    props.studentGroup
      ? props.studentGroup.code
      : t(
          'studentGroups.detailsTitle',
        ),
)

function formatDateTime(
  value: string | null,
): string {
  if (!value) {
    return '—'
  }

  return new Intl.DateTimeFormat(
    undefined,
    {
      dateStyle: 'medium',
      timeStyle: 'short',
    },
  ).format(
    new Date(value),
  )
}
</script>

<template>
  <BaseDialog
    v-model="visible"
    :title="dialogTitle"
    width="56rem"
  >
    <div
      v-if="studentGroup"
      class="
        student-group-details
      "
    >
      <section>
        <h3>
          {{
            t(
              'studentGroups.sections.general',
            )
          }}
        </h3>

        <dl>
          <div>
            <dt>
              {{
                t(
                  'studentGroups.fields.code',
                )
              }}
            </dt>

            <dd>
              {{
                studentGroup.code
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'studentGroups.fields.status',
                )
              }}
            </dt>

            <dd>
              <Tag
                :value="
                  studentGroup.is_active
                    ? t(
                        'studentGroups.active',
                      )
                    : t(
                        'studentGroups.inactive',
                      )
                "
                :severity="
                  studentGroup.is_active
                    ? 'success'
                    : 'secondary'
                "
              />
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'studentGroups.fields.admissionYear',
                )
              }}
            </dt>

            <dd>
              {{
                studentGroup
                  .admission_academic_year_name
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'studentGroups.fields.graduationYear',
                )
              }}
            </dt>

            <dd>
              {{
                studentGroup
                  .graduation_academic_year_name ||
                '—'
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'studentGroups.fields.studentCount',
                )
              }}
            </dt>

            <dd>
              {{
                studentGroup.student_count
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'studentGroups.fields.subgroupCount',
                )
              }}
            </dt>

            <dd>
              {{
                studentGroup.subgroup_count
              }}
            </dd>
          </div>
        </dl>
      </section>

      <section>
        <h3>
          {{
            t(
              'studentGroups.sections.education',
            )
          }}
        </h3>

        <dl>
          <div>
            <dt>
              {{
                t(
                  'studentGroups.fields.faculty',
                )
              }}
            </dt>

            <dd>
              {{
                studentGroup.faculty_name
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'studentGroups.fields.studyProgram',
                )
              }}
            </dt>

            <dd>
              {{
                studentGroup.study_program_name
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'studentGroups.fields.educationLevel',
                )
              }}
            </dt>

            <dd>
              {{
                studentGroup.education_level_name
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'studentGroups.fields.studyForm',
                )
              }}
            </dt>

            <dd>
              {{
                studentGroup.study_form_name
              }}
            </dd>
          </div>
        </dl>
      </section>

      <section>
        <h3>
          {{
            t(
              'studentGroups.sections.profiling',
            )
          }}
        </h3>

        <dl>
          <div>
            <dt>
              {{
                t(
                  'studentGroups.fields.profilingFaculty',
                )
              }}
            </dt>

            <dd>
              {{
                studentGroup
                  .profiling_department_faculty_name
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'studentGroups.fields.profilingDepartment',
                )
              }}
            </dt>

            <dd>
              {{
                studentGroup
                  .profiling_department_name
              }}
            </dd>
          </div>
        </dl>
      </section>

      <section
        v-if="
          studentGroup.notes
        "
      >
        <h3>
          {{
            t(
              'studentGroups.fields.notes',
            )
          }}
        </h3>

        <p>
          {{ studentGroup.notes }}
        </p>
      </section>

      <section>
        <h3>
          {{
            t(
              'studentGroups.sections.audit',
            )
          }}
        </h3>

        <dl>
          <div>
            <dt>
              {{
                t(
                  'studentGroups.fields.createdAt',
                )
              }}
            </dt>

            <dd>
              {{
                formatDateTime(
                  studentGroup.created_at,
                )
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'studentGroups.fields.createdBy',
                )
              }}
            </dt>

            <dd>
              {{
                studentGroup.created_by_name ||
                '—'
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'studentGroups.fields.updatedAt',
                )
              }}
            </dt>

            <dd>
              {{
                formatDateTime(
                  studentGroup.updated_at,
                )
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'studentGroups.fields.updatedBy',
                )
              }}
            </dt>

            <dd>
              {{
                studentGroup.updated_by_name ||
                '—'
              }}
            </dd>
          </div>
        </dl>
      </section>
    </div>
  </BaseDialog>
</template>

<style scoped>
.student-group-details {
  display: grid;
  gap: 1.5rem;
}

.student-group-details section {
  display: grid;
  gap: 0.75rem;
}

.student-group-details h3 {
  margin: 0;
  padding-bottom: 0.5rem;
  border-bottom:
    1px solid
    var(--app-border-color);
  font-size: 0.9rem;
}

.student-group-details dl {
  display: grid;
  grid-template-columns:
    repeat(
      2,
      minmax(0, 1fr)
    );
  margin: 0;
}

.student-group-details dl > div {
  padding: 0.65rem 0;
}

.student-group-details dt {
  color:
    var(--app-text-muted);
  font-size: 0.72rem;
}

.student-group-details dd {
  margin: 0.2rem 0 0;
  font-size: 0.82rem;
  font-weight: 600;
}

.student-group-details p {
  margin: 0;
  color:
    var(--app-text-muted);
  line-height: 1.6;
}

@media (max-width: 575px) {
  .student-group-details dl {
    grid-template-columns: 1fr;
  }
}
</style>
