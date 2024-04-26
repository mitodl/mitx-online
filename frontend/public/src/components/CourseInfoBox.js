import React from "react"
import {
  formatPrettyDate,
  emptyOrNil,
  getFlexiblePriceForProduct,
  formatLocalePrice,
  parseDateString,
  formatPrettyShortDate
} from "../lib/util"
import { getFirstRelevantRun } from "../lib/courseApi"
import moment from "moment-timezone"

import type { BaseCourseRun } from "../flow/courseTypes"
import { EnrollmentFlaggedCourseRun, RunEnrollment } from "../flow/courseTypes"
import type { CurrentUser } from "../flow/authTypes"

type CourseInfoBoxProps = {
  courses: Array<BaseCourseRun>,
  courseRuns: ?Array<EnrollmentFlaggedCourseRun>,
  enrollments: ?Array<RunEnrollment>,
  currentUser: CurrentUser,
  toggleUpgradeDialogVisibility: () => Promise<any>,
  setCurrentCourseRun: (run: EnrollmentFlaggedCourseRun) => Promise<any>
}

/**
 * This constructs the Date section for a given run
 * If the run is under the toggle "More Dates" the format is inline and month
 * is shortened to 3 letters.
 * @param {EnrollmentFlaggedCourseRun} run
 * @param {boolean} isArchived if the course ended, but still enrollable
 * @param {boolean} isMoreDates true if this run is going to show up under the More Dates toggle
 * */

const getCourseDates = (run, isArchived = false, isMoreDates = false) => {
  if (isArchived) {
    return (
      <>
        <span>Course content available anytime</span>
        <br />
        <b>Start:</b> {formatPrettyDate(parseDateString(run.start_date))}
      </>
    )
  }
  let startDate = isMoreDates
    ? formatPrettyShortDate(parseDateString(run.start_date))
    : formatPrettyDate(parseDateString(run.start_date))
  if (run.is_self_paced && moment(run.start_date).isBefore(moment())) {
    startDate = "Anytime"
  }
  return (
    <>
      <b>Start:</b> {startDate} {isMoreDates ? null : <br />}
      {run.end_date ? (
        <>
          <b>End:</b>{" "}
          {isMoreDates
            ? formatPrettyShortDate(parseDateString(run.end_date))
            : formatPrettyDate(parseDateString(run.end_date))}
        </>
      ) : null}
    </>
  )
}

export default class CourseInfoBox extends React.PureComponent<CourseInfoBoxProps> {
  state = {
    showMoreEnrollDates: false
  }
  toggleShowMoreEnrollDates() {
    this.setState({
      showMoreEnrollDates: !this.state.showMoreEnrollDates
    })
  }
  setRunEnrollDialog(run: EnrollmentFlaggedCourseRun) {
    this.props.setCurrentCourseRun(run)
    this.props.toggleUpgradeDialogVisibility()
  }

  warningMessage(isArchived) {
    const message = isArchived
      ? "This course is no longer active, but you can still access selected content."
      : "No sessions of this course are currently open for enrollment. More sessions may be added in the future."
    return (
      <div className="row d-flex align-self-stretch callout callout-warning course-archived-message">
        <i className="material-symbols-outlined warning">error</i>
        <p>{message}</p>
      </div>
    )
  }

  render() {
    const { courses, courseRuns } = this.props

    if (!courses || courses.length < 1) {
      return null
    }

    const course = courses[0]
    const run = getFirstRelevantRun(course, courseRuns)
    const product = run && run.products.length > 0 && run.products[0]
    const isArchived = run
      ? moment().isAfter(run.end_date) &&
        (moment().isBefore(run.enrollment_end) ||
          emptyOrNil(run.enrollment_end))
      : false

    const startDates = []
    const moreEnrollableCourseRuns = courseRuns && courseRuns.length > 1
    if (moreEnrollableCourseRuns) {
      courseRuns.forEach((courseRun, index) => {
        if (courseRun.id !== run.id) {
          startDates.push(
            <li key={index}>{getCourseDates(courseRun, isArchived, true)}</li>
          )
        }
      })
    }
    return (
      <>
        <div className="enrollment-info-box componentized">
          {!run || isArchived ? this.warningMessage(isArchived) : null}
          {run ? (
            <div className="row d-flex course-timing-message">
              <div
                className="enrollment-info-icon"
                aria-level="3"
                role="heading"
              >
                <img
                  src="/static/images/products/start-date.png"
                  alt="Course Timing"
                />
              </div>
              <div className="enrollment-info-text">
                {getCourseDates(run, isArchived)}
              </div>

              {!isArchived && moreEnrollableCourseRuns ? (
                <>
                  <button
                    className="info-link more-info more-dates"
                    onClick={() => this.toggleShowMoreEnrollDates()}
                  >
                    {this.state.showMoreEnrollDates
                      ? "Show Less"
                      : "More Dates"}
                  </button>
                  {this.state.showMoreEnrollDates ? (
                    <ul className="more-dates-enrollment-list">{startDates}</ul>
                  ) : null}
                </>
              ) : null}
            </div>
          ) : null}
          {run ? (
            <div className="row d-flex align-items-top">
              <div
                className="enrollment-info-icon"
                aria-level="3"
                role="heading"
              >
                <img
                  className="course-format-icon align-text-bottom"
                  src="/static/images/products/vector-left.png"
                  alt="Course Format"
                />
                <img
                  className="course-format-icon align-text-top"
                  src="/static/images/products/vector-right.png"
                  alt="Course Format"
                />
              </div>
              <div className="enrollment-info-text">
                <b>Course Format: </b>
                {isArchived || run.is_self_paced ? (
                  <>
                    Self-paced
                    <a
                      className="info-link more-info"
                      href="https://mitxonline.zendesk.com/hc/en-us/articles/21995114519067-What-are-Archived-courses-on-MITx-Online-"
                    >
                      What's this?
                    </a>
                  </>
                ) : (
                  <>
                    Instructor-paced
                    <a
                      className="info-link more-info"
                      href="https://mitxonline.zendesk.com/hc/en-us/articles/21994938130075-What-are-Instructor-Paced-courses-on-MITx-Online-"
                    >
                      What's this?
                    </a>
                  </>
                )}
              </div>
            </div>
          ) : null}
          {course && course.page ? (
            <div className="row d-flex align-items-top course-effort-message">
              <div
                className="enrollment-info-icon"
                aria-level="3"
                role="heading"
              >
                <img
                  src="/static/images/products/effort.png"
                  alt="Expected Length and Effort"
                />
              </div>
              <div className="enrollment-info-text">
                <b>Estimated: </b>
                {course.page.length}{" "}
                {course.page.effort ? (
                  <>
                    <div className="enrollment-effort">
                      {course.page.effort}
                    </div>
                  </>
                ) : null}
              </div>
            </div>
          ) : null}
          <div className="row d-flex align-items-center course-pricing-message">
            <div className="enrollment-info-icon" aria-level="3" role="heading">
              <img src="/static/images/products/cost.png" alt="Cost" />
            </div>
            <div className="enrollment-info-text">
              <b>Price: </b> <span>Free</span> to Learn
            </div>
          </div>
          <div className="row d-flex align-items-top">
            <div className="enrollment-info-text course-certificate-message">
              {run && product && !isArchived ? (
                <>
                  <span>Earn a Certificate: </span>
                  {formatLocalePrice(getFlexiblePriceForProduct(product))}
                  <a
                    className="info-link more-info"
                    target="_blank"
                    rel="noreferrer"
                    href="https://mitxonline.zendesk.com/hc/en-us/articles/16928404973979-Does-MITx-Online-offer-free-certificates-"
                  >
                    Learn more
                  </a>
                  {course.page.financial_assistance_form_url ? (
                    <a
                      className="info-link finaid-link"
                      target="_blank"
                      rel="noreferrer"
                      href={course.page.financial_assistance_form_url}
                    >
                      Financial assistance available
                    </a>
                  ) : null}
                  {run.upgrade_deadline ? (
                    <div className="text-danger">
                      Payment deadline:{" "}
                      {formatPrettyDate(moment(run.upgrade_deadline))}
                    </div>
                  ) : null}
                </>
              ) : (
                "No certificate available."
              )}
            </div>
          </div>
        </div>
        {course && course.programs && course.programs.length > 0 ? (
          <div className="program-info-box">
            <h3>
              Part of the following program
              {course.programs.length === 1 ? null : "s"}
            </h3>

            <ul>
              {course.programs.map(elem => (
                <li key={elem.readable_id}>
                  {" "}
                  <a
                    className="info-link"
                    href={`/programs/${elem.readable_id}/`}
                  >
                    {elem.title}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        ) : null}
      </>
    )
  }
}
