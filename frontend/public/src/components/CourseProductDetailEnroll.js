// @flow
import React, { Fragment } from "react"
import { createStructuredSelector } from "reselect"
import { pathOr } from "ramda"
import { compose } from "redux"
import { connect } from "react-redux"
import { connectRequest, mutateAsync } from "redux-query"
// $FlowFixMe
import { Modal, ModalBody, ModalHeader } from "reactstrap"

import Loader from "./Loader"
import { routes } from "../lib/urls"
import { getFlexiblePriceForProduct, formatLocalePrice } from "../lib/util"
import { EnrollmentFlaggedCourseRun, RunEnrollment } from "../flow/courseTypes"
import {
  courseRunsSelector,
  courseRunsQuery,
  courseRunsQueryKey,
  coursesSelector,
  coursesQuery,
  coursesQueryKey
} from "../lib/queries/courseRuns"
import {
  enrollmentsQuery,
  enrollmentsQueryKey,
  enrollmentsSelector
} from "../lib/queries/enrollment"

import { formatPrettyDate, emptyOrNil } from "../lib/util"
import moment from "moment-timezone"
import {
  getFirstRelevantRun,
  isFinancialAssistanceAvailable,
  isWithinEnrollmentPeriod
} from "../lib/courseApi"
import { getCookie } from "../lib/api"
import users, { currentUserSelector } from "../lib/queries/users"
import {
  enrollmentMutation,
  deactivateEnrollmentMutation
} from "../lib/queries/enrollment"
import { checkFeatureFlag } from "../lib/util"
import AddlProfileFieldsForm from "./forms/AddlProfileFieldsForm"
import CourseInfoBox from "./CourseInfoBox"

import type { User } from "../flow/authTypes"
import type { Product } from "../flow/cartTypes"

type Props = {
  courseId: ?string,
  isLoading: ?boolean,
  courseRuns: ?Array<EnrollmentFlaggedCourseRun>,
  courses: ?Array<any>,
  enrollments: ?Array<RunEnrollment>,
  status: ?number,
  courseIsLoading: ?boolean,
  courseStatus: ?number,
  enrollmentsIsLoading: ?boolean,
  enrollmentsStatus: ?number,
  upgradeEnrollmentDialogVisibility: boolean,
  addProductToBasket: (user: number, productId: number) => Promise<any>,
  currentUser: User,
  createEnrollment: (runId: number) => Promise<any>,
  deactivateEnrollment: (runId: number) => Promise<any>,
  updateAddlFields: (currentUser: User) => Promise<any>,
  forceRequest: () => any
}
type ProductDetailState = {
  upgradeEnrollmentDialogVisibility: boolean,
  showAddlProfileFieldsModal: boolean,
  currentCourseRun: ?EnrollmentFlaggedCourseRun,
  destinationUrl: string
}

export class CourseProductDetailEnroll extends React.Component<
  Props,
  ProductDetailState
> {
  state = {
    upgradeEnrollmentDialogVisibility: false,
    currentCourseRun:                  null,
    showAddlProfileFieldsModal:        false,
    destinationUrl:                    ""
  }

  resolveCurrentRun() {
    const { courseRuns } = this.props

    return !this.getCurrentCourseRun() && courseRuns
      ? courseRuns[0]
      : this.getCurrentCourseRun()
  }

  toggleAddlProfileFieldsModal() {
    this.setState({
      showAddlProfileFieldsModal: !this.state.showAddlProfileFieldsModal
    })

    if (
      !this.state.showAddlProfileFieldsModal &&
      this.state.destinationUrl.length > 0
    ) {
      const target = this.state.destinationUrl
      this.setState({
        destinationUrl: ""
      })
      window.open(target, "_blank")
    }
  }

  redirectToCourseHomepage(url: string, ev: any) {
    /*
    If we've got addl_field_flag, then display the extra info modal. Otherwise,
    send the learner directly to the page.
    */

    const { currentUser, updateAddlFields } = this.props

    if (currentUser.user_profile && currentUser.user_profile.addl_field_flag) {
      return
    }

    ev.preventDefault()

    this.setState({
      destinationUrl:             url,
      showAddlProfileFieldsModal: true
    })

    updateAddlFields(currentUser)
  }

  async saveProfile(profileData: User, { setSubmitting }: Object) {
    const { updateAddlFields } = this.props

    try {
      await updateAddlFields(profileData)
    } finally {
      setSubmitting(false)
      this.toggleAddlProfileFieldsModal()
    }
  }

  async checkForExistingEnrollment(run: EnrollmentFlaggedCourseRun) {
    // Find an existing enrollment - the default should be the audit enrollment
    // already have, so you can just upgrade in place. If you don't, you get the
    // current run (which should be the first available one).
    const { enrollments } = this.props

    if (enrollments) {
      const firstAuditEnrollment = enrollments.find(
        (enrollment: RunEnrollment) =>
          enrollment.run.course.id === run.course.id &&
          enrollment.enrollment_mode === "audit"
      )

      if (firstAuditEnrollment) {
        this.setCurrentCourseRun(firstAuditEnrollment.run)
        return
      }
    }

    this.setCurrentCourseRun(run)
  }

  toggleUpgradeDialogVisibility = () => {
    const { upgradeEnrollmentDialogVisibility } = this.state
    const run = this.resolveCurrentRun()

    if (!upgradeEnrollmentDialogVisibility) {
      this.checkForExistingEnrollment(run)
    } else {
      window.location = "/dashboard/"
    }

    this.setState({
      upgradeEnrollmentDialogVisibility: !upgradeEnrollmentDialogVisibility
    })
  }

  setCurrentCourseRun = (courseRun: EnrollmentFlaggedCourseRun) => {
    this.setState({
      currentCourseRun: courseRun
    })
  }

  hndSetCourseRun = (event: any) => {
    const { courseRuns } = this.props

    const matchingCourseRun =
      courseRuns &&
      courseRuns.find(
        (elem: EnrollmentFlaggedCourseRun) =>
          elem.id === parseInt(event.target.value)
      )

    if (matchingCourseRun) {
      this.setCurrentCourseRun(matchingCourseRun)
    }
  }

  getCurrentCourseRun = (): EnrollmentFlaggedCourseRun => {
    return this.state.currentCourseRun
  }

  getFirstUnenrolledCourseRun = (): EnrollmentFlaggedCourseRun => {
    const { courseRuns } = this.props

    return courseRuns
      ? courseRuns.find(
        (run: EnrollmentFlaggedCourseRun) =>
          run.is_enrolled === false &&
            moment(run.enrollment_start) <= moment.now()
      ) || courseRuns[0]
      : null
  }

  cancelEnrollment() {
    const { upgradeEnrollmentDialogVisibility } = this.state

    this.setState({
      upgradeEnrollmentDialogVisibility: !upgradeEnrollmentDialogVisibility
    })
  }

  renderRunSelectorButtons(run: EnrollmentFlaggedCourseRun) {
    const { courseRuns } = this.props

    return (
      <>
        {courseRuns && courseRuns.length > 1 ? (
          <label htmlFor="choose-courserun">Choose a date:</label>
        ) : (
          <label htmlFor="choose-courserun">
            There is one session available:
          </label>
        )}
        <select
          onChange={this.hndSetCourseRun.bind(this)}
          className="form-control"
        >
          {courseRuns &&
            courseRuns
              .filter((elem: EnrollmentFlaggedCourseRun) => elem.is_upgradable)
              .map((elem: EnrollmentFlaggedCourseRun) => (
                <option
                  selected={run.id === elem.id}
                  value={elem.id}
                  key={`courserun-selection-${elem.id}`}
                >
                  {formatPrettyDate(moment(new Date(elem.start_date)))} -{" "}
                  {formatPrettyDate(moment(new Date(elem.end_date)))}
                </option>
              ))}
        </select>
      </>
    )
  }

  getEnrollmentForm(run: EnrollmentFlaggedCourseRun, showNewDesign: boolean) {
    const csrfToken = getCookie("csrftoken")

    return showNewDesign ? (
      <form action="/enrollments/" method="post">
        <input type="hidden" name="csrfmiddlewaretoken" value={csrfToken} />
        <input type="hidden" name="run" value={run ? run.id : ""} />
        <button type="submit" className="btn enroll-now enroll-now-free">
          <strong>Enroll for Free</strong> without a certificate
        </button>
      </form>
    ) : (
      <div className="d-flex">
        <div className="flex-grow-1 w-auto">
          <form action="/enrollments/" method="post">
            <input type="hidden" name="csrfmiddlewaretoken" value={csrfToken} />
            <input type="hidden" name="run" value={run ? run.id : ""} />
            <button type="submit" className="btn enroll-now enroll-now-free">
              No thanks, I'll take the course for free without a certificate
            </button>
          </form>
        </div>
        <div className="ml-auto">
          <button
            onClick={this.cancelEnrollment.bind(this)}
            className="btn enroll-now enroll-now-free cancel-enrollment-button"
          >
            Cancel Enrollment
          </button>
        </div>
      </div>
    )
  }

  updateDate(run: EnrollmentFlaggedCourseRun) {
    // for original design - not used in course infobox design
    let date = emptyOrNil(run.start_date)
      ? undefined
      : moment(new Date(run.start_date))
    date = date ? date.utc() : date
    const dateElem = document.getElementById("start_date")
    if (dateElem) {
      dateElem.innerHTML = `<strong>${formatPrettyDate(date)}</strong>`
    }
  }

  renderUpgradeEnrollmentDialog(showNewDesign: boolean) {
    const { courseRuns, courses } = this.props
    const run = this.resolveCurrentRun()

    const course =
      courses && courses.find((elem: any) => elem.id === run.course.id)
    const needFinancialAssistanceLink =
      isFinancialAssistanceAvailable(run) &&
      !run.approved_flexible_price_exists ? (
          <p className="financial-assistance-link">
            <a
              href={
                course && course.page && course.page.financial_assistance_form_url
              }
            >
            Need financial assistance?
            </a>
          </p>
        ) : null
    const { upgradeEnrollmentDialogVisibility } = this.state
    const product = run.products ? run.products[0] : null
    const upgradableCourseRuns = courseRuns
      ? courseRuns.filter(
        (run: EnrollmentFlaggedCourseRun) => run.is_upgradable
      )
      : []

    return product ? (
      showNewDesign ? (
        <Modal
          id={`upgrade-enrollment-dialog`}
          className="upgrade-enrollment-modal"
          isOpen={upgradeEnrollmentDialogVisibility}
          toggle={() => this.cancelEnrollment()}
          centered
        >
          <ModalHeader toggle={() => this.cancelEnrollment()}>
            {run.title}
          </ModalHeader>
          <ModalBody>
            {upgradableCourseRuns.length > 1 ? (
              <div className="row date-selector-button-bar">
                <div className="col-12">
                  <div>{this.renderRunSelectorButtons(run)}</div>
                </div>
              </div>
            ) : null}

            <div className="row upsell-messaging-header">
              <div className="col-12 p-0 font-weight-bold">
                Do you want to earn a certificate?
              </div>
            </div>

            <div className="row d-sm-flex flex-md-row flex-sm-column">
              <div className="col-md-6 col-sm-12">
                <ul>
                  <li> Certificate is signed by MIT faculty</li>
                  <li>
                    {" "}
                    Demonstrates knowledge and skills taught in this course
                  </li>
                  <li> Enhance your college &amp; earn a promotion</li>
                </ul>
              </div>
              <div className="col-md-6 col-sm-12">
                <ul>
                  <li>Highlight on your resume/CV</li>
                  <li>Share on your social channels &amp; LinkedIn</li>
                  <li>
                    Enhance your college application with an earned certificate
                    from MIT
                  </li>
                </ul>
              </div>
            </div>

            <div className="row certificate-pricing-row d-sm-flex flex-md-row flex-sm-column">
              <div className="col-md-6 col-sm-12 certificate-pricing d-flex align-items-center">
                <div className="certificate-pricing-logo">
                  <img src="/static/images/certificates/certificate-logo.svg" />
                </div>
                <p>
                  Certificate track:{" "}
                  <strong id="certificate-price-info">
                    {product &&
                      formatLocalePrice(getFlexiblePriceForProduct(product))}
                  </strong>
                  {run.upgrade_deadline ? (
                    <>
                      <br />
                      <span className="text-danger">
                        Payment date:{" "}
                        {formatPrettyDate(moment(run.upgrade_deadline))}
                      </span>
                    </>
                  ) : null}
                </p>
              </div>
              <div className="col-md-6 col-sm-12 pr-0 enroll-and-pay">
                <form action="/cart/add/" method="get" className="text-center">
                  <input type="hidden" name="product_id" value={product.id} />
                  <button type="submit" className="btn btn-upgrade">
                    <strong>Enroll and Pay</strong>
                    <br />
                    <span>for the certificate track</span>
                  </button>
                </form>
              </div>
            </div>

            <div className="row upgrade-options-row">
              <div>{needFinancialAssistanceLink}</div>
              <div>{this.getEnrollmentForm(run, showNewDesign)}</div>
            </div>
          </ModalBody>
        </Modal>
      ) : (
        <Modal
          id={`upgrade-enrollment-dialog`}
          className="upgrade-enrollment-modal"
          isOpen={upgradeEnrollmentDialogVisibility}
          toggle={() => this.toggleUpgradeDialogVisibility()}
        >
          <ModalHeader toggle={() => this.toggleUpgradeDialogVisibility()}>
            Enroll
          </ModalHeader>
          <ModalBody>
            <div className="row modal-subheader d-flex">
              <div className="flex-grow-1 align-self-end">
                Learn online and get a certificate
              </div>
              <div className="text-end align-self-end">
                {formatLocalePrice(getFlexiblePriceForProduct(product))}
              </div>
            </div>
            <div className="row">
              <div className="col-12">
                <p>
                  Thank you for choosing an MITx Online course. By paying for
                  this course, you're joining the most engaged and motivated
                  learners on your path to a certificate from MITx.
                </p>

                <p>
                  Your certificate is signed by MIT faculty and demonstrates
                  that you have gained the knowledge and skills taught in this
                  course. Showcase your certificate on your resume and social
                  channels to advance your career, earn a promotion, or enhance
                  your college applications.
                </p>

                <form action="/cart/add/" method="get" className="text-center">
                  <input type="hidden" name="product_id" value={product.id} />
                  <button
                    type="submit"
                    className="btn btn-primary btn-gradient-red"
                  >
                    Continue
                  </button>
                </form>
                {needFinancialAssistanceLink}
              </div>
            </div>
            <div className="cancel-link">
              {this.getEnrollmentForm(run, showNewDesign)}
            </div>
            <div className="faq-link">
              <a
                href="https://mitxonline.zendesk.com/hc/en-us"
                target="_blank"
                rel="noreferrer"
              >
                FAQs
              </a>
            </div>
          </ModalBody>
        </Modal>
      )
    ) : null
  }

  renderAddlProfileFieldsModal() {
    const { currentUser } = this.props
    const { showAddlProfileFieldsModal } = this.state

    return (
      <Modal
        id={`upgrade-enrollment-dialog`}
        className="upgrade-enrollment-modal"
        isOpen={showAddlProfileFieldsModal}
        toggle={() => this.toggleAddlProfileFieldsModal()}
      >
        <ModalHeader
          id={`more-info-modal-${currentUser.id}`}
          toggle={() => this.toggleAddlProfileFieldsModal()}
        >
          Provide More Info
        </ModalHeader>
        <ModalBody>
          <div className="row">
            <div className="col-12">
              <p>
                To help us with our education research missions, please tell us
                more about yourself.
              </p>
            </div>
          </div>

          <AddlProfileFieldsForm
            onSubmit={this.saveProfile.bind(this)}
            onCancel={() => this.toggleAddlProfileFieldsModal()}
            user={currentUser}
            requireTypeFields={true}
          ></AddlProfileFieldsForm>
        </ModalBody>
      </Modal>
    )
  }

  renderEnrolledButton(run: EnrollmentFlaggedCourseRun) {
    const startDate =
      run && !emptyOrNil(run.start_date)
        ? moment(new Date(run.start_date))
        : null
    const waitingForCourseToBeginMessage = moment().isBefore(startDate) ? (
      <p style={{ fontSize: "16px" }}>
        Enrolled and waiting for the course to begin.
      </p>
    ) : null
    const disableEnrolledBtn = moment().isBefore(startDate) ? "disabled" : ""

    return run && run.is_enrolled ? (
      <>
        <Fragment>
          {run.courseware_url ? (
            <a
              href={run.courseware_url}
              onClick={ev =>
                run ? this.redirectToCourseHomepage(run.courseware_url, ev) : ev
              }
              className={`btn btn-primary btn-enrollment-button btn-gradient-red highlight outline ${disableEnrolledBtn}`}
              target="_blank"
              rel="noopener noreferrer"
            >
              Enrolled &#10003;
            </a>
          ) : (
            <div
              className={`btn btn-primary btn-enrollment-button btn-gradient-red highlight outline ${disableEnrolledBtn}`}
            >
              Enrolled &#10003;
            </div>
          )}
          {waitingForCourseToBeginMessage}
        </Fragment>
      </>
    ) : null
  }

  renderEnrollLoginButton() {
    const { currentUser } = this.props

    return !currentUser || !currentUser.id ? (
      <h2>
        <a
          href={routes.login}
          className="btn btn-primary btn-enrollment-button btn-lg btn-gradient-red highlight"
        >
          Enroll now
        </a>
      </h2>
    ) : null
  }

  renderEnrollNowButton(
    run: EnrollmentFlaggedCourseRun,
    product: Product | null
  ) {
    const { currentUser } = this.props
    const csrfToken = getCookie("csrftoken")

    return currentUser &&
      currentUser.id &&
      run &&
      !run.is_enrolled &&
      isWithinEnrollmentPeriod(run) ? (
        <h2>
          {product && run.is_upgradable ? (
            <button
              id="upgradeEnrollBtn"
              className="btn btn-primary btn-enrollment-button btn-lg btn-gradient-red highlight enroll-now"
              onClick={() => this.toggleUpgradeDialogVisibility()}
            >
            Enroll now
            </button>
          ) : (
            <form action="/enrollments/" method="post">
              <input type="hidden" name="csrfmiddlewaretoken" value={csrfToken} />
              <input type="hidden" name="run" value={run ? run.id : ""} />
              <button
                type="submit"
                className="btn btn-primary btn-enrollment-button btn-gradient-red highlight enroll-now"
              >
              Enroll now
              </button>
            </form>
          )}
        </h2>
      ) : null
  }

  render() {
    const {
      courseRuns,
      isLoading,
      courses,
      courseIsLoading,
      currentUser,
      enrollments,
      enrollmentsIsLoading
    } = this.props
    const showNewDesign = checkFeatureFlag(
      "mitxonline-new-product-page",
      currentUser && currentUser.id ? currentUser.id : "anonymousUser"
    )

    let run,
      product = null

    if (courses && courseRuns) {
      run = getFirstRelevantRun(courses[0], courseRuns)

      if (run) {
        product = run && run.products ? run.products[0] : null
        this.updateDate(run)
      }
    }

    return run ? (
      <>
        {
          // $FlowFixMe: isLoading null or undefined
          <Loader key="product_detail_enroll_loader" isLoading={isLoading}>
            <>
              {this.renderEnrolledButton(run)}
              {this.renderEnrollLoginButton()}
              {this.renderEnrollNowButton(run, product)}

              {currentUser ? this.renderAddlProfileFieldsModal() : null}
              {run ? this.renderUpgradeEnrollmentDialog(showNewDesign) : null}
            </>
          </Loader>
        }
        {showNewDesign ? (
          <>
            {
              // $FlowFixMe: isLoading null or undefined
              <Loader
                key="course_info_loader"
                isLoading={courseIsLoading || enrollmentsIsLoading}
              >
                <CourseInfoBox
                  courses={courses}
                  courseRuns={courseRuns}
                  currentUser={currentUser}
                  toggleUpgradeDialogVisibility={
                    this.toggleUpgradeDialogVisibility
                  }
                  setCurrentCourseRun={this.setCurrentCourseRun}
                  enrollments={enrollments}
                ></CourseInfoBox>
              </Loader>
            }
          </>
        ) : null}
      </>
    ) : null
  }
}

const createEnrollment = (run: EnrollmentFlaggedCourseRun) =>
  mutateAsync(enrollmentMutation(run.id))

const deactivateEnrollment = (run: number) =>
  mutateAsync(deactivateEnrollmentMutation(run))

const updateAddlFields = (currentUser: User) => {
  const updatedUser = {
    name:          currentUser.name,
    email:         currentUser.email,
    legal_address: currentUser.legal_address,
    user_profile:  {
      ...currentUser.user_profile,
      addl_field_flag: true
    }
  }

  return mutateAsync(users.editProfileMutation(updatedUser))
}

const mapStateToProps = createStructuredSelector({
  courseRuns:           courseRunsSelector,
  courses:              coursesSelector,
  currentUser:          currentUserSelector,
  enrollments:          enrollmentsSelector,
  isLoading:            pathOr(true, ["queries", courseRunsQueryKey, "isPending"]),
  courseIsLoading:      pathOr(true, ["queries", coursesQueryKey, "isPending"]),
  enrollmentsIsLoading: pathOr(true, [
    "queries",
    enrollmentsQueryKey,
    "isPending"
  ]),
  status:            pathOr(null, ["queries", courseRunsQueryKey, "status"]),
  courseStatus:      pathOr(true, ["queries", coursesQueryKey, "status"]),
  enrollmentsStatus: pathOr(true, ["queries", enrollmentsQueryKey, "status"])
})

const mapPropsToConfig = props => [
  courseRunsQuery(props.courseId),
  coursesQuery(props.courseId),
  enrollmentsQuery(),
  users.currentUserQuery()
]

const mapDispatchToProps = {
  createEnrollment,
  deactivateEnrollment,
  updateAddlFields
}

export default compose(
  connect(mapStateToProps, mapDispatchToProps),
  connectRequest(mapPropsToConfig)
)(CourseProductDetailEnroll)
