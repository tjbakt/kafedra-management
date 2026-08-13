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
  Curriculum,
} from '@/modules/curricula/types'

const visible =
  defineModel<boolean>({
    default: false,
  })

const props =
  defineProps<{
    curriculum:
      Curriculum | null
  }>()

const { t } = useI18n()

const title = computed(
  () =>
    props.curriculum
      ? props.curriculum.code
      : t(
          'curricula.detailsTitle',
        ),
)

function statusLabel(
  status: Curriculum['status'],
): string {
  return t(
    `curricula.statuses.${status}`,
  )
}

function statusSeverity(
  status: Curriculum['status'],
):
  | 'success'
  | 'secondary'
  | 'warn' {
  if (status === 'approved') {
    return 'success'
  }

  if (status === 'archived') {
    return 'secondary'
  }

  return 'warn'
}

function formatDate(
  value: string | null,
): string {
  if (!value) {
    return '—'
  }

  return new Intl.DateTimeFormat(
    undefined,
    {
      dateStyle: 'medium',
    },
  ).format(
    new Date(
      `${value}T00:00:00`,
    ),
  )
}

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
    :title="title"
    width="58rem"
  >
    <div
      v-if="curriculum"
      class="
        curriculum-details
      "
    >
      <section>
        <h3>
          {{
            t(
              'curricula.sections.general',
            )
          }}
        </h3>

        <dl>
          <div>
            <dt>
              {{
                t(
                  'curricula.fields.code',
                )
              }}
            </dt>

            <dd>
              {{ curriculum.code }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'curricula.fields.version',
                )
              }}
            </dt>

            <dd>
              {{ curriculum.version }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'curricula.fields.studyProgram',
                )
              }}
            </dt>

            <dd>
              {{ curriculum.study_program_code }}
              —
              {{ curriculum.study_program_name }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'curricula.fields.educationLevel',
                )
              }}
            </dt>

            <dd>
              {{
                curriculum.education_level_name
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'curricula.fields.studyForm',
                )
              }}
            </dt>

            <dd>
              {{
                curriculum.study_form_name
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'curricula.fields.effectiveAcademicYear',
                )
              }}
            </dt>

            <dd>
              {{
                curriculum
                  .effective_academic_year_name
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'curricula.fields.semestersCount',
                )
              }}
            </dt>

            <dd>
              {{
                curriculum.semesters_count ??
                '—'
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'curricula.fields.disciplinesCount',
                )
              }}
            </dt>

            <dd>
              {{
                curriculum.disciplines_count
              }}
            </dd>
          </div>
        </dl>
      </section>

      <section>
        <h3>
          {{
            t(
              'curricula.sections.approval',
            )
          }}
        </h3>

        <dl>
          <div>
            <dt>
              {{
                t(
                  'curricula.fields.status',
                )
              }}
            </dt>

            <dd>
              <Tag
                :value="
                  statusLabel(
                    curriculum.status,
                  )
                "
                :severity="
                  statusSeverity(
                    curriculum.status,
                  )
                "
              />
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'curricula.fields.active',
                )
              }}
            </dt>

            <dd>
              <Tag
                :value="
                  curriculum.is_active
                    ? t('common.yes')
                    : t('common.no')
                "
                :severity="
                  curriculum.is_active
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
                  'curricula.fields.approvedAt',
                )
              }}
            </dt>

            <dd>
              {{
                formatDate(
                  curriculum.approved_at,
                )
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'curricula.fields.approvalDocument',
                )
              }}
            </dt>

            <dd>
              {{
                curriculum.approval_document ||
                '—'
              }}
            </dd>
          </div>
        </dl>
      </section>

      <section
        v-if="curriculum.notes"
      >
        <h3>
          {{
            t(
              'curricula.fields.notes',
            )
          }}
        </h3>

        <p>
          {{ curriculum.notes }}
        </p>
      </section>

      <section>
        <h3>
          {{
            t(
              'curricula.sections.audit',
            )
          }}
        </h3>

        <dl>
          <div>
            <dt>
              {{
                t(
                  'curricula.fields.createdAt',
                )
              }}
            </dt>

            <dd>
              {{
                formatDateTime(
                  curriculum.created_at,
                )
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'curricula.fields.createdBy',
                )
              }}
            </dt>

            <dd>
              {{
                curriculum.created_by_name ||
                '—'
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'curricula.fields.updatedAt',
                )
              }}
            </dt>

            <dd>
              {{
                formatDateTime(
                  curriculum.updated_at,
                )
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'curricula.fields.updatedBy',
                )
              }}
            </dt>

            <dd>
              {{
                curriculum.updated_by_name ||
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
.curriculum-details {
  display: grid;
  gap: 1.5rem;
}

.curriculum-details section {
  display: grid;
  gap: 0.75rem;
}

.curriculum-details h3 {
  margin: 0;
  padding-bottom: 0.5rem;
  border-bottom:
    1px solid
    var(--app-border-color);
  font-size: 0.9rem;
}

.curriculum-details dl {
  display: grid;
  grid-template-columns:
    repeat(
      2,
      minmax(0, 1fr)
    );
  margin: 0;
}

.curriculum-details dl > div {
  padding: 0.65rem 0;
}

.curriculum-details dt {
  color:
    var(--app-text-muted);
  font-size: 0.72rem;
}

.curriculum-details dd {
  margin: 0.2rem 0 0;
  font-size: 0.82rem;
  font-weight: 600;
}

.curriculum-details p {
  margin: 0;
  white-space: pre-wrap;
  color:
    var(--app-text-muted);
  line-height: 1.6;
}

@media (max-width: 575px) {
  .curriculum-details dl {
    grid-template-columns:
      1fr;
  }
}
</style>
