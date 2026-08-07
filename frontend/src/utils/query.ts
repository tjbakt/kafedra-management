import type {
  ApiListParams,
} from '@/types/api'

export function cleanQueryParams(
  params: ApiListParams,
): ApiListParams {
  return Object.fromEntries(
    Object.entries(params).filter(
      ([, value]) =>
        value !== undefined &&
        value !== null &&
        value !== '',
    ),
  )
}

export function buildOrdering(
  field:
    | string
    | undefined,
  order:
    | number
    | null
    | undefined,
): string {
  if (!field || !order) {
    return ''
  }

  return order === -1
    ? `-${field}`
    : field
}
