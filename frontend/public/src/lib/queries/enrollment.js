import { pathOr } from "ramda"

import { getCsrfOptions, nextState } from "./util"
import { emptyOrNil } from "../util"

export const enrollmentsSelector = pathOr(null, ["entities", "enrollments"])
export const enrollmentSelector = pathOr(null, ["entities", "enrollment"])
export const programEnrollmentsSelector = pathOr(null, [
  "entities",
  "program_enrollments"
])

export const enrollmentsQueryKey = "enrollments"
export const enrollmentQueryKey = "enrollment"
export const programEnrollmentsQueryKey = "program_enrollments"

export const enrollmentsQuery = () => ({
  queryKey:  enrollmentsQueryKey,
  url:       "/api/enrollments/",
  transform: json => ({
    enrollments: json
  }),
  update: {
    enrollments: nextState
  }
})

export const programEnrollmentsQuery = () => ({
  queryKey:  programEnrollmentsQueryKey,
  url:       "/api/program_enrollments/",
  transform: json => ({
    program_enrollments: json
  }),
  update: {
    program_enrollments: nextState
  }
})

export const enrollmentQuery = () => ({
  queryKey:  enrollmentQuery,
  url:       "/api/enrollments/${enrollmentId}",
  transform: json => ({
    enrollment: json
  }),
  update: {
    enrollment: nextState
  }
})

export const deactivateEnrollmentMutation = (enrollmentId: number) => ({
  url:     `/api/enrollments/${enrollmentId}/`,
  options: {
    ...getCsrfOptions(),
    method: "DELETE"
  },
  update: {
    enrollments: prevEnrollments => {
      return emptyOrNil(prevEnrollments)
        ? []
        : prevEnrollments.filter(enrollment => enrollment.id !== enrollmentId)
    },
    program_enrollments: prevProgramEnrollments => {
      return emptyOrNil(prevProgramEnrollments)
        ? []
        : prevProgramEnrollments.map(programEnrollment => {
          return {
            ...programEnrollment,
            enrollments: programEnrollment.enrollments.filter(
              enrollment => enrollment.id !== enrollmentId
            )
          }
        })
    }
  }
})

export const courseEmailsSubscriptionMutation = (
  enrollmentId: number,
  emailsSubscription: string = ""
) => ({
  url:  `/api/enrollments/${enrollmentId}/`,
  body: {
    receive_emails: emailsSubscription
  },
  options: {
    ...getCsrfOptions(),
    method: "PATCH"
  },
  update: {
    enrollments: prevEnrollments => {
      if (!emptyOrNil(prevEnrollments)) {
        prevEnrollments.find(
          enrollment => enrollment.id === enrollmentId
        ).edx_emails_subscription = emailsSubscription ? true : false
      } else {
        prevEnrollments = []
      }
      return prevEnrollments
    }
  }
})
