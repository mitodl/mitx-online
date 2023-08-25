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
import { EnrollmentFlaggedCourseRun } from "../flow/courseTypes"
import {
  courseRunsSelector,
  courseRunsQuery,
  courseRunsQueryKey,
  programsSelector,
  programsQuery,
  programsQueryKey
} from "../lib/queries/courseRuns"
import {
  programEnrollmentsQuery,
  programEnrollmentsQueryKey,
  programEnrollmentsSelector
} from "../lib/queries/enrollment"

import { formatPrettyDate, emptyOrNil } from "../lib/util"
import moment from "moment-timezone"
import {
  isFinancialAssistanceAvailable,
  isWithinEnrollmentPeriod
} from "../lib/courseApi"
import { getCookie } from "../lib/api"
import type { User } from "../flow/authTypes"
import users, { currentUserSelector } from "../lib/queries/users"
import { enrollmentMutation } from "../lib/queries/enrollment"
import { checkFeatureFlag } from "../lib/util"
import AddlProfileFieldsForm from "./forms/AddlProfileFieldsForm"
import ProgramInfoBox from "./ProgramInfoBox"
import type { ProgramEnrollment } from "../flow/courseTypes"

type Props = {
  programId: ?string,
  isLoading: ?boolean,
  courseRuns: ?Array<EnrollmentFlaggedCourseRun>,
  status: ?number,
  programs: ?Array<any>,
  programIsLoading: ?boolean,
  programStatus: ?number,
  upgradeEnrollmentDialogVisibility: boolean,
  addProductToBasket: (user: number, productId: number) => Promise<any>,
  currentUser: User,
  createEnrollment: (runId: number) => Promise<any>,
  updateAddlFields: (currentUser: User) => Promise<any>,
  programEnrollments: ?Array<ProgramEnrollment>,
  programEnrollmentsLoading: ?boolean
}
type ProductDetailState = {
  upgradeEnrollmentDialogVisibility: boolean,
  showAddlProfileFieldsModal: boolean,
  currentCourseRun: ?EnrollmentFlaggedCourseRun,
  destinationUrl: string
}

export class ProductDetailEnrollApp extends React.Component<
  Props,
  ProductDetailState
> {
  state = {
    upgradeEnrollmentDialogVisibility: false,
    currentCourseRun:                  null,
    showAddlProfileFieldsModal:        false,
    destinationUrl:                    ""
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

    if (
      !checkFeatureFlag("enable_addl_profile_fields") ||
      (currentUser.user_profile && currentUser.user_profile.addl_field_flag)
    ) {
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

  toggleUpgradeDialogVisibility = () => {
    const { upgradeEnrollmentDialogVisibility } = this.state
    // const { createEnrollment, courseRuns } = this.props
    // const run =
    //   !this.getCurrentCourseRun() && courseRuns
    //     ? courseRuns[0]
    //     : this.getCurrentCourseRun()

    // if (!upgradeEnrollmentDialogVisibility) {
    //   createEnrollment(run)
    // } else {
    //   window.location = "/dashboard/"
    // }

    this.setState({
      upgradeEnrollmentDialogVisibility: !upgradeEnrollmentDialogVisibility
    })
  }

  setCurrentCourseRun = (runId: string) => {
    const { courseRuns } = this.props

    const courserun = courseRuns.find(run => run.courseware_id === runId)

    this.setState({
      currentCourseRun: courserun
    })
  }

  getCurrentCourseRun = (): EnrollmentFlaggedCourseRun => {
    return this.state.currentCourseRun
  }

  renderCertificateInfoPanel() {
    const { currentCourseRun: run } = this.state

    const product = run.products ? run.products[0] : null
    const needFinancialAssistanceLink =
      isFinancialAssistanceAvailable(run) &&
      !run.approved_flexible_price_exists ? (
          <p className="financial-assistance-link">
            <a href={run.page.financial_assistance_form_url}>
            Need financial assistance?
            </a>
          </p>
        ) : null

    return (
      <>
        <div className="row certificate-pricing-row">
          <div className="col-6 certificate-pricing">
            <p>
              Certitficate track:{" "}
              <strong>${product && formatLocalePrice(product.price)}</strong>
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

            <p>{needFinancialAssistanceLink}</p>
          </div>
          <div className="col-6">
            <form action="/cart/add/" method="get" className="text-center">
              <input type="hidden" name="product_id" value={product.id} />
              <button type="submit" className="btn btn-upgrade">
                <strong>Continue</strong>
                <br />
                on the certificate track
              </button>
            </form>
          </div>
        </div>

        <div className="cancel-link">{this.getEnrollmentForm(run)}</div>
      </>
    )
  }

  renderUpgradeEnrollmentDialog() {
    const { programs } = this.props

    const { upgradeEnrollmentDialogVisibility } = this.state

    const program = programs[0]
    const courseRuns = []

    const { currentCourseRun } = this.state

    program.courses.forEach(course => {
      if (course.next_run_id) {
        course.courseruns.forEach(run => {
          if (course.next_run_id === run.id) {
            courseRuns.push(run)
          }
        })
      } else {
        if (course.courseruns.length > 0) {
          courseRuns.push(course.courseruns[0])
        }
      }
    })

    return (
      <Modal
        id={`upgrade-enrollment-dialog`}
        className="upgrade-enrollment-modal"
        isOpen={upgradeEnrollmentDialogVisibility}
        toggle={() => this.toggleUpgradeDialogVisibility()}
        centered
      >
        <ModalHeader toggle={() => this.toggleUpgradeDialogVisibility()}>
          {program.title}
        </ModalHeader>
        <ModalBody>
          <div className="row">
            <div className="col-12">
              <p>
                Thank you for choosing an MITx online course. By paying for this
                course, you're joining the most engaged and motivated learners
                on your path to a certificate from MITx.
              </p>
            </div>
          </div>

          <div className="row">
            <div className="col-12">
              <div className="form-group">
                <label
                  htmlFor="program-course-selection"
                  className="text-strong"
                >
                  Select Course
                </label>
                <select
                  className="form-control"
                  name="program-course-selection"
                  onChange={ev => this.setCurrentCourseRun(ev.target.value)}
                >
                  <option></option>
                  {courseRuns.map(run => (
                    <option
                      key={`selectable-courserun-${run.id}`}
                      value={run.courseware_id}
                    >
                      {run.courseware_id} - {run.title}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          <div className="row">
            <div className="col-12">
              <p className="acheiving-text">
                Acheiving a certificate has its advantages:
              </p>
            </div>
          </div>

          <div className="row">
            <div className="col-6">
              <ul>
                <li> Certificate is signed by MIT faculty</li>
                <li>
                  {" "}
                  Demonstrates knowledge and skills taught in this course
                </li>
                <li> Enhance your college &amp; earn a promotion</li>
              </ul>
            </div>
            <div className="col-6">
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

          {currentCourseRun ? <>{this.renderCertificateInfoPanel()}</> : null}
        </ModalBody>
      </Modal>
    )
  }

  getEnrollmentForm(run) {
    const csrfToken = getCookie("csrftoken")

    return (
      <form action="/enrollments/" method="post">
        <input type="hidden" name="csrfmiddlewaretoken" value={csrfToken} />
        <input type="hidden" name="run" value={run ? run.id : ""} />
        <button type="submit" className="btn enroll-now enroll-now-free">
          No thanks, I'll take the free version
        </button>
      </form>
    )
  }

  updateDate(run: EnrollmentFlaggedCourseRun) {
    let date = emptyOrNil(run.start_date)
      ? undefined
      : moment(new Date(run.start_date))
    date = date ? date.utc() : date
    const dateElem = document.getElementById("start_date")
    if (dateElem) {
      dateElem.innerHTML = `<strong>${formatPrettyDate(date)}</strong>`
    }
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

  render() {
    const {
      programs,
      programIsLoading,
      currentUser,
      programEnrollments,
      programEnrollmentsLoading
    } = this.props

    const showNewDesign = checkFeatureFlag("mitxonline-new-product-page")

    let enrollment = undefined

    if (!programEnrollmentsLoading) {
      enrollment = programEnrollments.find(
        (elem: ProgramEnrollment) => elem.program.id === programs[0].id
      )
    }

    return (
      <>
        {
          // $FlowFixMe: programEnrollmentsLoading null or undefined
          <Loader
            key="product_detail_enroll_loader"
            isLoading={programEnrollmentsLoading}
          >
            <>
              {enrollment ? (
                <Fragment>
                  <div
                    className={`btn btn-primary btn-enrollment-button btn-gradient-red highlight outline`}
                  >
                    Enrolled &#10003;
                  </div>
                </Fragment>
              ) : (
                <Fragment>
                  {currentUser && !currentUser.id ? (
                    <a
                      href={routes.login}
                      className="btn btn-primary btn-enrollment-button btn-lg btn-gradient-red highlight"
                    >
                      Enroll now
                    </a>
                  ) : (
                    <Fragment>
                      <button
                        className="btn btn-primary btn-enrollment-button btn-gradient-red highlight enroll-now"
                        onClick={this.toggleUpgradeDialogVisibility}
                      >
                        Enroll now button
                      </button>
                    </Fragment>
                  )}
                </Fragment>
              )}

              {currentUser ? this.renderAddlProfileFieldsModal() : null}
              {programs ? this.renderUpgradeEnrollmentDialog() : null}
            </>
          </Loader>
        }
        {showNewDesign ? (
          <>
            {
              // $FlowFixMe: isLoading null or undefined
              <Loader key="course_info_loader" isLoading={programIsLoading}>
                <ProgramInfoBox programs={programs}></ProgramInfoBox>
              </Loader>
            }
          </>
        ) : null}
      </>
    )
  }
}

const createEnrollment = (run: EnrollmentFlaggedCourseRun) =>
  mutateAsync(enrollmentMutation(run.id))

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
  courseRuns:                courseRunsSelector,
  programs:                  programsSelector,
  currentUser:               currentUserSelector,
  programEnrollments:        programEnrollmentsSelector,
  isLoading:                 pathOr(true, ["queries", courseRunsQueryKey, "isPending"]),
  programIsLoading:          pathOr(true, ["queries", programsQueryKey, "isPending"]),
  status:                    pathOr(null, ["queries", courseRunsQueryKey, "status"]),
  programStatus:             pathOr(true, ["queries", programsQueryKey, "status"]),
  programEnrollmentsLoading: pathOr(true, [
    "queries",
    programEnrollmentsQueryKey,
    "isPending"
  ])
})

const mapPropsToConfig = props => [
  courseRunsQuery(props.programId),
  programsQuery(props.programId),
  programEnrollmentsQuery(),
  users.currentUserQuery()
]

const mapDispatchToProps = {
  createEnrollment,
  updateAddlFields
}

export default compose(
  connect(mapStateToProps, mapDispatchToProps),
  connectRequest(mapPropsToConfig)
)(ProductDetailEnrollApp)
