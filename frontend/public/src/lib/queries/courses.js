import { pathOr } from "ramda"

import { nextState } from "./util"

export const coursesSelector = pathOr(null, ["entities", "courses", "results"])

export const coursesNextPageSelector = pathOr(null, [
  "entities",
  "courses",
  "next"
])

export const coursesQueryKey = "courses"

export const coursesQuery = (page, ids) => ({
  queryKey:  coursesQueryKey,
  url:       ids.length > 0 ? `/api/courses/?page=${page}&live=true&page__live=true&courserun_is_enrollable=true&id=${ids.toString()}` : `/api/courses/?page=${page}&live=true&page__live=true&courserun_is_enrollable=true`,
  transform: json => ({
    courses: json
  }),
  update: {
    courses: nextState
  }
})
