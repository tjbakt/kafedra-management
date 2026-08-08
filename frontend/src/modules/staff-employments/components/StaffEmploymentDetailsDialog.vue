<script setup lang="ts">
import Tag from 'primevue/tag'

import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import BaseDialog from '@/components/base/BaseDialog.vue'

import type {
  StaffEmployment,
} from '@/modules/staff-employments/types'

const visible =
  defineModel<boolean>({
    default: false,
  })

const props =
  defineProps<{
    employment: StaffEmployment | null
  }>()

const { t } = useI18n()

const dialogTitle = computed(
  () =>
    props.employment
      ? props.employment
          .staff_member_name
      : t(
          'staffEmployments.detailsTitle',
        ),
)

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

function employmentTypeLabel(
  value: string,
): string {
  const keyMap:
    Record<string, string> = {
      primary:
        'staffEmployments.types.primary',

      internal_part_time:
        'staffEmployments.types.internalPartTime',

      external_part_time:
        'staffEmployments.types.externalPartTime',

      hourly:
        'staffEmployments.types.hourly',
    }

  return t(
    keyMap[value] ??
      'staffEmployments.types.primary',
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
      v-if="employment"
      class="
        employment-details
      "
    >
      <section>
        <h3>
          {{
            t(
              'staffEmployments.sections.assignment',
            )
          }}
        </h3>

        <dl>
          <div>
            <dt>
              {{
                t(
                  'staffEmployments.fields.staffMember',
                )
              }}
            </dt>

            <dd>
              {{
                employment.staff_member_name
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'staffEmployments.fields.department',
                )
              }}
            </dt>

            <dd>
              {{
                employment.department_name
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'staffEmployments.fields.faculty',
                )
              }}
            </dt>

            <dd>
              {{
                employment.faculty_name
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'staffEmployments.fields.position',
                )
              }}
            </dt>

            <dd>
              {{
                employment.position_name
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'staffEmployments.fields.employmentType',
                )
              }}
            </dt>

            <dd>
              {{
                employmentTypeLabel(
                  employment.employment_type,
                )
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'staffEmployments.fields.rate',
                )
              }}
            </dt>

            <dd>
              {{ employment.rate }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'staffEmployments.fields.primary',
                )
              }}
            </dt>

            <dd>
              <Tag
                :value="
                  employment.is_primary
                    ? t('common.yes')
                    : t('common.no')
                "
                :severity="
                  employment.is_primary
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
                  'staffEmployments.fields.status',
                )
              }}
            </dt>

            <dd>
              <Tag
                :value="
                  employment.is_active
                    ? t(
                        'staffEmployments.active',
                      )
                    : t(
                        'staffEmployments.inactive',
                      )
                "
                :severity="
                  employment.is_active
                    ? 'success'
                    : 'secondary'
                "
              />
            </dd>
          </div>
        </dl>
      </section>

      <section>
        <h3>
          {{
            t(
              'staffEmployments.sections.period',
            )
          }}
        </h3>

        <dl>
          <div>
            <dt>
              {{
                t(
                  'staffEmployments.fields.startDate',
                )
              }}
            </dt>

            <dd>
              {{
                formatDate(
                  employment.start_date,
                )
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'staffEmployments.fields.endDate',
                )
              }}
            </dt>

            <dd>
              {{
                formatDate(
                  employment.end_date,
                )
              }}
            </dd>
          </div>
        </dl>
      </section>

      <section>
        <h3>
          {{
            t(
              'staffEmployments.sections.document',
            )
          }}
        </h3>

        <dl>
          <div>
            <dt>
              {{
                t(
                  'staffEmployments.fields.documentNumber',
                )
              }}
            </dt>

            <dd>
              {{
                employment.document_number ||
                '—'
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'staffEmployments.fields.documentDate',
                )
              }}
            </dt>

            <dd>
              {{
                formatDate(
                  employment.document_date,
                )
              }}
            </dd>
          </div>
        </dl>
      </section>

      <section
        v-if="
          employment.notes
        "
      >
        <h3>
          {{
            t(
              'staffEmployments.fields.notes',
            )
          }}
        </h3>

        <p>
          {{ employment.notes }}
        </p>
      </section>

      <section>
        <h3>
          {{
            t(
              'staffEmployments.sections.audit',
            )
          }}
        </h3>

        <dl>
          <div>
            <dt>
              {{
                t(
                  'staffEmployments.fields.createdAt',
                )
              }}
            </dt>

            <dd>
              {{
                formatDateTime(
                  employment.created_at,
                )
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'staffEmployments.fields.createdBy',
                )
              }}
            </dt>

            <dd>
              {{
                employment.created_by_name ||
                '—'
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'staffEmployments.fields.updatedAt',
                )
              }}
            </dt>

            <dd>
              {{
                formatDateTime(
                  employment.updated_at,
                )
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'staffEmployments.fields.updatedBy',
                )
              }}
            </dt>

            <dd>
              {{
                employment.updated_by_name ||
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
.employment-details {
  display: grid;
  gap: 1.5rem;
}

.employment-details section {
  display: grid;
  gap: 0.75rem;
}

.employment-details h3 {
  margin: 0;
  padding-bottom: 0.5rem;
  border-bottom:
    1px solid
    var(--app-border-color);
  font-size: 0.9rem;
}

.employment-details dl {
  display: grid;
  grid-template-columns:
    repeat(
      2,
      minmax(0, 1fr)
    );
  margin: 0;
}

.employment-details dl > div {
  padding: 0.65rem 0;
}

.employment-details dt {
  color:
    var(--app-text-muted);
  font-size: 0.72rem;
}

.employment-details dd {
  margin: 0.2rem 0 0;
  font-size: 0.82rem;
  font-weight: 600;
}

.employment-details p {
  margin: 0;
  color:
    var(--app-text-muted);
  line-height: 1.6;
}

@media (max-width: 575px) {
  .employment-details dl {
    grid-template-columns: 1fr;
  }
}
</style>
