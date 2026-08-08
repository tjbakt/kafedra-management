<script setup lang="ts">
import Tag from 'primevue/tag'

import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import BaseDialog from '@/components/base/BaseDialog.vue'

import type {
  StaffMember,
} from '@/modules/staff/types'

const visible =
  defineModel<boolean>({
    default: false,
  })

const props =
  defineProps<{
    staffMember: StaffMember | null
  }>()

const { t } = useI18n()

const title = computed(
  () =>
    props.staffMember
      ? props.staffMember.full_name
      : t('staff.detailsTitle'),
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
</script>

<template>
  <BaseDialog
    v-model="visible"
    :title="title"
    width="55rem"
  >
    <div
      v-if="staffMember"
      class="staff-details"
    >
      <section>
        <h3>
          {{
            t(
              'staff.sections.personal',
            )
          }}
        </h3>

        <dl>
          <div>
            <dt>
              {{
                t(
                  'staff.fields.personnelNumber',
                )
              }}
            </dt>

            <dd>
              {{
                staffMember.personnel_number
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'staff.fields.fullName',
                )
              }}
            </dt>

            <dd>
              {{
                staffMember.full_name
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'staff.fields.gender',
                )
              }}
            </dt>

            <dd>
              {{
                staffMember.gender ===
                'male'
                  ? t(
                      'staff.genderMale',
                    )
                  : staffMember.gender ===
                      'female'
                    ? t(
                        'staff.genderFemale',
                      )
                    : '—'
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'staff.fields.birthDate',
                )
              }}
            </dt>

            <dd>
              {{
                formatDate(
                  staffMember.birth_date,
                )
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'staff.fields.status',
                )
              }}
            </dt>

            <dd>
              <Tag
                :value="
                  staffMember.is_active
                    ? t(
                        'staff.working',
                      )
                    : t(
                        'staff.notWorking',
                      )
                "
                :severity="
                  staffMember.is_active
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
                  'staff.fields.username',
                )
              }}
            </dt>

            <dd>
              {{
                staffMember.username ||
                '—'
              }}
            </dd>
          </div>
        </dl>
      </section>

      <section>
        <h3>
          {{
            t(
              'staff.sections.contacts',
            )
          }}
        </h3>

        <dl>
          <div>
            <dt>
              {{
                t(
                  'staff.fields.phone',
                )
              }}
            </dt>

            <dd>
              {{
                staffMember.phone ||
                '—'
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'staff.fields.email',
                )
              }}
            </dt>

            <dd>
              {{
                staffMember.email ||
                '—'
              }}
            </dd>
          </div>
        </dl>
      </section>

      <section>
        <h3>
          {{
            t(
              'staff.sections.academic',
            )
          }}
        </h3>

        <dl>
          <div>
            <dt>
              {{
                t(
                  'staff.fields.academicDegree',
                )
              }}
            </dt>

            <dd>
              {{
                staffMember.academic_degree_name ||
                '—'
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'staff.fields.degreeDate',
                )
              }}
            </dt>

            <dd>
              {{
                formatDate(
                  staffMember.degree_awarded_date,
                )
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'staff.fields.academicTitle',
                )
              }}
            </dt>

            <dd>
              {{
                staffMember.academic_title_name ||
                '—'
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'staff.fields.titleDate',
                )
              }}
            </dt>

            <dd>
              {{
                formatDate(
                  staffMember.title_awarded_date,
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
              'staff.sections.employments',
            )
          }}
        </h3>

        <div
          v-if="
            staffMember.employments.length
          "
          class="employment-list"
        >
          <article
            v-for="
              employment in
                staffMember.employments
            "
            :key="
              employment.id
            "
            class="employment-card"
          >
            <div>
              <strong>
                {{
                  employment.department_name
                }}
              </strong>

              <span>
                {{
                  employment.position_name
                }}
              </span>
            </div>

            <div>
              <Tag
                :value="
                  employment.employment_type_name
                "
                severity="info"
              />

              <span>
                {{
                  employment.rate
                }}
                {{
                  t(
                    'staff.rateShort',
                  )
                }}
              </span>
            </div>
          </article>
        </div>

        <p
          v-else
          class="staff-details__empty"
        >
          {{
            t(
              'staff.noEmployments',
            )
          }}
        </p>
      </section>

      <section
        v-if="staffMember.notes"
      >
        <h3>
          {{
            t(
              'staff.fields.notes',
            )
          }}
        </h3>

        <p
          class="staff-details__notes"
        >
          {{
            staffMember.notes
          }}
        </p>
      </section>

      <section>
        <h3>
          {{
            t(
              'staff.sections.audit',
            )
          }}
        </h3>

        <dl>
          <div>
            <dt>
              {{
                t(
                  'staff.fields.createdAt',
                )
              }}
            </dt>

            <dd>
              {{
                formatDateTime(
                  staffMember.created_at,
                )
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'staff.fields.createdBy',
                )
              }}
            </dt>

            <dd>
              {{
                staffMember.created_by_name ||
                '—'
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'staff.fields.updatedAt',
                )
              }}
            </dt>

            <dd>
              {{
                formatDateTime(
                  staffMember.updated_at,
                )
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'staff.fields.updatedBy',
                )
              }}
            </dt>

            <dd>
              {{
                staffMember.updated_by_name ||
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
.staff-details {
  display: grid;
  gap: 1.5rem;
}

.staff-details section {
  display: grid;
  gap: 0.75rem;
}

.staff-details h3 {
  margin: 0;
  padding-bottom: 0.5rem;
  border-bottom:
    1px solid
    var(--app-border-color);
  font-size: 0.9rem;
}

.staff-details dl {
  display: grid;
  grid-template-columns:
    repeat(
      2,
      minmax(0, 1fr)
    );
  margin: 0;
}

.staff-details dl > div {
  padding: 0.65rem 0;
}

.staff-details dt {
  color:
    var(--app-text-muted);
  font-size: 0.72rem;
}

.staff-details dd {
  margin: 0.2rem 0 0;
  font-size: 0.82rem;
  font-weight: 600;
}

.employment-list {
  display: grid;
  gap: 0.6rem;
}

.employment-card {
  display: flex;
  align-items: center;
  justify-content:
    space-between;
  gap: 1rem;
  padding: 0.85rem;
  border:
    1px solid
    var(--app-border-color);
  border-radius:
    var(--app-radius);
}

.employment-card > div {
  display: flex;
  align-items: center;
  gap: 0.7rem;
}

.employment-card > div:first-child {
  display: grid;
  gap: 0.2rem;
}

.employment-card strong {
  font-size: 0.82rem;
}

.employment-card span {
  color:
    var(--app-text-muted);
  font-size: 0.75rem;
}

.staff-details__empty,
.staff-details__notes {
  margin: 0;
  color:
    var(--app-text-muted);
  font-size: 0.82rem;
  line-height: 1.6;
}

@media (max-width: 575px) {
  .staff-details dl {
    grid-template-columns: 1fr;
  }

  .employment-card {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
