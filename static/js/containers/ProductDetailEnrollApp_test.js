// @flow
import { assert } from "chai"

import IntegrationTestHelper from "../util/integration_test_helper"
import ProductDetailEnrollApp, {
  ProductDetailEnrollApp as InnerProductDetailEnrollApp
} from "./ProductDetailEnrollApp"

import { courseRunsSelector } from "../lib/queries/courseRuns"
import {
  makeCourseRunDetail,
  makeCourseRunEnrollment
} from "../factories/course"

import * as courseApi from "../lib/courseApi"

import moment from "moment"

describe("ProductDetailEnrollApp", () => {
  let helper, renderPage, isWithinEnrollmentPeriodStub

  beforeEach(() => {
    helper = new IntegrationTestHelper()

    renderPage = helper.configureHOCRenderer(
      ProductDetailEnrollApp,
      InnerProductDetailEnrollApp,
      {},
      {}
    )

    isWithinEnrollmentPeriodStub = helper.sandbox.stub(
      courseApi,
      "isWithinEnrollmentPeriod"
    )
  })

  afterEach(() => {
    helper.cleanup()
  })

  it("renders a Loader component", async () => {
    const { inner } = await renderPage({
      queries: {
        courseRuns: {
          isPending: true
        }
      }
    })

    assert.isTrue(inner.props().isLoading)
    const loader = inner.find("Loader")
    assert.isOk(loader.exists())
    assert.isTrue(loader.props().isLoading)
  })

  it("checks for enroll now button", async () => {
    const courseRun = makeCourseRunDetail()
    isWithinEnrollmentPeriodStub.returns(true)
    const { inner } = await renderPage(
      {
        entities: {
          courseRuns: [courseRun]
        },
        queries: {
          courseRuns: {
            isPending: false,
            status:    200
          }
        }
      },
      {}
    )
    assert.equal(
      inner
        .find("button")
        .at(0)
        .text(),
      "Enroll now"
    )
  })

  it("checks for enroll now button should not appear if enrollment start in future", async () => {
    const courseRun = makeCourseRunDetail()
    isWithinEnrollmentPeriodStub.returns(false)
    const { inner } = await renderPage(
      {
        entities: {
          courseRuns: [courseRun]
        },
        queries: {
          courseRuns: {
            isPending: false,
            status:    200
          }
        }
      },
      {}
    )

    assert.isNotOk(
      inner
        .find("button")
        .at(0)
        .exists()
    )
  })

  it("checks for enroll now button should appear if enrollment start not in future", async () => {
    const courseRun = makeCourseRunDetail()
    isWithinEnrollmentPeriodStub.returns(true)
    const { inner } = await renderPage(
      {
        entities: {
          courseRuns: [courseRun]
        },
        queries: {
          courseRuns: {
            isPending: false,
            status:    200
          }
        }
      },
      {}
    )

    assert.equal(
      inner
        .find("button")
        .at(0)
        .text(),
      "Enroll now"
    )
  })

  it("checks for enrolled button", async () => {
    const userEnrollment = makeCourseRunEnrollment()
    const expectedResponse = {
      ...userEnrollment.run,
      is_enrolled: true
    }

    const { inner, store } = await renderPage(
      {
        entities: {
          courseRuns: [expectedResponse]
        },
        queries: {
          courseRuns: {
            isPending: false,
            status:    200
          }
        }
      },
      {}
    )

    assert.equal(
      inner
        .find("a")
        .at(0)
        .text(),
      "Enrolled ✓"
    )
    assert.equal(courseRunsSelector(store.getState())[0], expectedResponse)
  })
})
