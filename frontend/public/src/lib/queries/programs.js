import { pathOr } from "ramda"

import { nextState } from "./util"

export const programsSelector = pathOr(null, [
  "entities",
  "programs",
  "results"
])

export const programsNextPageSelector = pathOr(null, [
  "entities",
  "programs",
  "next"
])

export const programsCountSelector = pathOr(null, [
  "entities",
  "programs",
  "count"
])

export const programsQueryKey = "programs"

export const programsQuery = (page, ids) => ({
  queryKey:  programsQueryKey,
  url:       ids.length > 0 ? `/api/v2/programs/?page=${page}&live=true&page__live=true&id=${ids}` : `/api/v2/programs/?page=${page}&live=true&page__live=true`,
  transform: json => ({
    programs: json
  }),
  update: {
    programs: nextState
  }
})
