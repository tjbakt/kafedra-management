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
  StudyProgram,
} from '@/modules/study-programs/types'

const visible =
  defineModel<boolean>({
    default: false,
  })

const props =
  defineProps<{
    studyProgram:
      StudyProgram | null
  }>()

const { t } = useI18n()

const dialogTitle = computed(
  () =>
    props.studyProgram
      ? `${props.studyProgram.code} — ${props.studyProgram.display_name}`
      : t(
          'studyPrograms.detailsTitle',
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
    width="52rem"
  >
    <div
      v-if="studyProgram"
      class="
        study-program-details
      "
    >
      <section>
        <h3>
          {{
            t(
              'studyPrograms.sections.general',
            )
          }}
        </h3>

        <dl>
          <div>
            <dt>
              {{
                t(
                  'studyPrograms.fields.code',
                )
              }}
            </dt>

            <dd>
              {{
                studyProgram.code
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'studyPrograms.fields.status',
                )
              }}
            </dt>

            <dd>
              <Tag
                :value="
                  studyProgram.is_active
                    ? t(
                        'studyPrograms.active',
                      )
                    : t(
                        'studyPrograms.inactive',
                      )
                "
                :severity="
                  studyProgram.is_active
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
                  'studyPrograms.fields.nameRu',
                )
              }}
            </dt>

            <dd>
              {{
                studyProgram.name_ru
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'studyPrograms.fields.nameUz',
                )
              }}
            </dt>

            <dd>
              {{
                studyProgram.name_uz
              }}
            </dd>
          </div>
        </dl>
      </section>

      <section>
        <h3>
          {{
            t(
              'studyPrograms.sections.structure',
            )
          }}
        </h3>

        <dl>
          <div>
            <dt>
              {{
                t(
                  'studyPrograms.fields.university',
                )
              }}
            </dt>

            <dd>
              {{
                studyProgram.university_name
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'studyPrograms.fields.educationLevel',
                )
              }}
            </dt>

            <dd>
              {{
                studyProgram.education_level_name
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'studyPrograms.fields.profilingFaculty',
                )
              }}
            </dt>

            <dd>
              {{
                studyProgram.profiling_faculty_name
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'studyPrograms.fields.profilingDepartment',
                )
              }}
            </dt>

            <dd>
              {{
                studyProgram.profiling_department_name
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'studyPrograms.fields.sortOrder',
                )
              }}
            </dt>

            <dd>
              {{
                studyProgram.sort_order
              }}
            </dd>
          </div>
        </dl>
      </section>

      <section>
        <h3>
          {{
            t(
              'studyPrograms.sections.audit',
            )
          }}
        </h3>

        <dl>
          <div>
            <dt>
              {{
                t(
                  'studyPrograms.fields.createdAt',
                )
              }}
            </dt>

            <dd>
              {{
                formatDateTime(
                  studyProgram.created_at,
                )
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'studyPrograms.fields.createdBy',
                )
              }}
            </dt>

            <dd>
              {{
                studyProgram.created_by_name ||
                '—'
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'studyPrograms.fields.updatedAt',
                )
              }}
            </dt>

            <dd>
              {{
                formatDateTime(
                  studyProgram.updated_at,
                )
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'studyPrograms.fields.updatedBy',
                )
              }}
            </dt>

            <dd>
              {{
                studyProgram.updated_by_name ||
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
.study-program-details {
  display: grid;
  gap: 1.5rem;
}

.study-program-details section {
  display: grid;
  gap: 0.75rem;
}

.study-program-details h3 {
  margin: 0;
  padding-bottom: 0.5rem;
  border-bottom:
    1px solid
    var(--app-border-color);
  font-size: 0.9rem;
}

.study-program-details dl {
  display: grid;
  grid-template-columns:
    repeat(
      2,
      minmax(0, 1fr)
    );
  margin: 0;
}

.study-program-details dl > div {
  padding: 0.65rem 0;
}

.study-program-details dt {
  color:
    var(--app-text-muted);
  font-size: 0.72rem;
}

.study-program-details dd {
  margin: 0.2rem 0 0;
  font-size: 0.82rem;
  font-weight: 600;
}

@media (max-width: 575px) {
  .study-program-details dl {
    grid-template-columns: 1fr;
  }
}
</style>
