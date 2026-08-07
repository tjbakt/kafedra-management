<script setup lang="ts">
import Tag from 'primevue/tag'

import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import BaseDialog from '@/components/base/BaseDialog.vue'

import type {
  Department,
} from '@/modules/departments/types'

const visible =
  defineModel<boolean>({
    default: false,
  })

const props =
  defineProps<{
    department: Department | null
  }>()

const { t } = useI18n()

const title = computed(
  () =>
    props.department
      ? `${props.department.code} — ${props.department.display_name}`
      : t(
          'departments.detailsTitle',
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
    width="48rem"
  >
    <div
      v-if="department"
      class="department-details"
    >
      <section>
        <h3>
          {{
            t(
              'departments.sections.general',
            )
          }}
        </h3>

        <dl>
          <div>
            <dt>
              {{
                t(
                  'departments.fields.code',
                )
              }}
            </dt>

            <dd>
              {{
                department.code
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'departments.fields.nameRu',
                )
              }}
            </dt>

            <dd>
              {{
                department.name_ru
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'departments.fields.nameUz',
                )
              }}
            </dt>

            <dd>
              {{
                department.name_uz
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'departments.fields.faculty',
                )
              }}
            </dt>

            <dd>
              {{
                department.faculty_name
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'departments.fields.university',
                )
              }}
            </dt>

            <dd>
              {{
                department.university_name
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'departments.fields.status',
                )
              }}
            </dt>

            <dd>
              <Tag
                :value="
                  department.is_active
                    ? t(
                        'departments.active',
                      )
                    : t(
                        'departments.inactive',
                      )
                "
                :severity="
                  department.is_active
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
              'departments.sections.contacts',
            )
          }}
        </h3>

        <dl>
          <div>
            <dt>
              {{
                t(
                  'departments.fields.head',
                )
              }}
            </dt>

            <dd>
              {{
                department.head_name ||
                '—'
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'departments.fields.phone',
                )
              }}
            </dt>

            <dd>
              {{
                department.phone ||
                '—'
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'departments.fields.email',
                )
              }}
            </dt>

            <dd>
              {{
                department.email ||
                '—'
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'departments.fields.room',
                )
              }}
            </dt>

            <dd>
              {{
                department.room ||
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
              'departments.sections.audit',
            )
          }}
        </h3>

        <dl>
          <div>
            <dt>
              {{
                t(
                  'departments.fields.createdAt',
                )
              }}
            </dt>

            <dd>
              {{
                formatDate(
                  department.created_at,
                )
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'departments.fields.createdBy',
                )
              }}
            </dt>

            <dd>
              {{
                department.created_by_name ||
                '—'
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'departments.fields.updatedAt',
                )
              }}
            </dt>

            <dd>
              {{
                formatDate(
                  department.updated_at,
                )
              }}
            </dd>
          </div>

          <div>
            <dt>
              {{
                t(
                  'departments.fields.updatedBy',
                )
              }}
            </dt>

            <dd>
              {{
                department.updated_by_name ||
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
.department-details {
  display: grid;
  gap: 1.5rem;
}

.department-details section {
  display: grid;
  gap: 0.75rem;
}

.department-details h3 {
  margin: 0;
  padding-bottom: 0.5rem;
  border-bottom:
    1px solid
    var(--app-border-color);
  font-size: 0.9rem;
}

.department-details dl {
  display: grid;
  grid-template-columns:
    repeat(
      2,
      minmax(0, 1fr)
    );
  margin: 0;
  gap: 0;
}

.department-details dl > div {
  padding: 0.7rem 0;
}

.department-details dt {
  color:
    var(--app-text-muted);
  font-size: 0.72rem;
}

.department-details dd {
  margin: 0.2rem 0 0;
  font-size: 0.82rem;
  font-weight: 600;
}

@media (max-width: 575px) {
  .department-details dl {
    grid-template-columns: 1fr;
  }
}
</style>
