// @flow
import { expect } from "chai"
import moment from "moment-timezone"
import IntegrationTestHelper from "../../util/integration_test_helper"
import CatalogPage, { CatalogPage as InnerCatalogPage } from "./CatalogPage"
import { formatPrettyDate } from "../../lib/util"

const displayedCourse = {
  id:          2,
  title:       "E2E Test Course",
  readable_id: "course-v1:edX+E2E-101",
  courseruns:  [
    {
      title:            "E2E Test Course",
      start_date:       moment(),
      end_date:         moment().add(2, "M"),
      enrollment_start: moment(),
      enrollment_end:   null,
      expiration_date:  null,
      courseware_url:
        "http://edx.odl.local:18000/courses/course-v1:edX+E2E-101+course/",
      courseware_id:    "course-v1:edX+E2E-101+course",
      upgrade_deadline: null,
      is_upgradable:    true,
      is_self_paced:    false,
      run_tag:          "course",
      id:               2,
      live:             true,
      products:         [
        {
          id:                     1,
          price:                  "999.00",
          description:            "course-v1:edX+E2E-101+course",
          is_active:              true,
          product_flexible_price: {
            amount:          null,
            automatic:       false,
            discount_type:   null,
            redemption_type: null,
            max_redemptions: null,
            discount_code:   "",
            payment_type:    null,
            activation_date: null,
            expiration_date: null
          }
        }
      ],
      page: {
        feature_image_src:             "/static/images/mit-dome.png",
        page_url:                      "/courses/course-v1:edX+E2E-101/",
        financial_assistance_form_url: "",
        description:                   "E2E Test Course",
        current_price:                 999.0,
        instructors:                   [],
        live:                          true
      },
      approved_flexible_price_exists: false
    }
  ],
  next_run_id: 2,
  departments: [
    {
      name: "Science"
    }
  ],
  page: {
    feature_image_src:             "/static/images/mit-dome.png",
    page_url:                      "/courses/course-v1:edX+E2E-101/",
    financial_assistance_form_url: "",
    description:                   "E2E Test Course",
    current_price:                 999.0,
    instructors:                   [],
    live:                          true
  }
}

const displayedProgram = {
  title:       "P2",
  readable_id: "P2",
  id:          2,
  courses:     [
    {
      id:          1,
      title:       "Demonstration Course",
      readable_id: "course-v1:edX+DemoX",
      courseruns:  [
        {
          title:            "Demonstration Course",
          start_date:       moment(),
          end_date:         moment().add(2, "M"),
          enrollment_start: null,
          enrollment_end:   null,
          expiration_date:  null,
          courseware_url:
            "http://edx.odl.local:18000/courses/course-v1:edX+DemoX+Demo_Course/",
          courseware_id:    "course-v1:edX+DemoX+Demo_Course",
          upgrade_deadline: null,
          is_upgradable:    true,
          is_self_paced:    true,
          run_tag:          "Demo_Course",
          id:               1,
          live:             true,
          products:         [
            {
              id:                     2,
              price:                  "999.00",
              description:            "course-v1:edX+DemoX+Demo_Course",
              is_active:              true,
              product_flexible_price: null
            }
          ],
          page: {
            feature_image_src:             "/static/images/mit-dome.png",
            page_url:                      "/courses/course-v1:edX+DemoX/",
            financial_assistance_form_url:
              "/courses/course-v1:edX+DemoX/data-economics-and-development-policy-financial-assistance-form/",
            description:   "Demonstration Course",
            current_price: null,
            instructors:   [],
            live:          true
          },
          approved_flexible_price_exists: false
        }
      ],
      next_run_id: null,
      departments: [
        {
          name: "History"
        }
      ],
      page: {
        feature_image_src:             "/static/images/mit-dome.png",
        page_url:                      "/courses/course-v1:edX+DemoX/",
        financial_assistance_form_url:
          "/courses/course-v1:edX+DemoX/data-economics-and-development-policy-financial-assistance-form/",
        description:   "Demonstration Course",
        current_price: null,
        instructors:   [],
        live:          true
      },
      feature_image_src:             "/static/images/mit-dome.png",
      page_url:                      "/courses/course-v1:edX+DemoX/",
      financial_assistance_form_url:
        "/courses/course-v1:edX+DemoX/data-economics-and-development-policy-financial-assistance-form/",
      description:   "Demonstration Course",
      current_price: null,
      instructors:   [],
      live:          true
    }
  ],
  requirements: {
    required:  [1],
    electives: []
  },
  req_tree: [
    {
      data: {
        node_type:      "program_root",
        operator:       null,
        operator_value: null,
        program:        2,
        course:         null,
        title:          "",
        elective_flag:  false
      },
      id:       4,
      children: [
        {
          data: {
            node_type:      "operator",
            operator:       "all_of",
            operator_value: null,
            program:        2,
            course:         null,
            title:          "Required Courses",
            elective_flag:  false
          },
          id:       5,
          children: [
            {
              data: {
                node_type:      "course",
                operator:       null,
                operator_value: null,
                program:        2,
                course:         1,
                title:          null,
                elective_flag:  false
              },
              id: 6
            }
          ]
        }
      ]
    }
  ],
  page: {
    feature_image_src:
      "http://mitxonline.odl.local:8013/static/images/mit-dome.png"
  },
  program_type: "Series",
  departments:  [
    {
      name: "Science"
    }
  ],
  live: true
}

describe("CatalogPage", () => {
  const mockIntersectionObserver = class {
    constructor() {}
    observe() {}
    unobserve() {}
    disconnect() {}
  }
  let helper, courses, programs, renderPage

  beforeEach(() => {
    // Mock the intersection observer.
    helper = new IntegrationTestHelper()
    window.IntersectionObserver = mockIntersectionObserver

    renderPage = helper.configureHOCRenderer(CatalogPage, InnerCatalogPage)
  })

  afterEach(() => {
    helper.cleanup()
  })

  it("default state is set when catalog renders", async () => {
    courses = [displayedCourse]
    const { inner } = await renderPage(
      {
        queries: {
          courses: {
            isPending: false,
            status:    200
          }
        },
        entities: {
          courses: courses
        }
      },
      {}
    )
    inner.instance().componentDidUpdate({}, {})
    expect(inner.state().selectedDepartment).equals("All Departments")
    expect(inner.state().tabSelected).equals("courses")
    expect(inner.state().numberCatalogRowsToDisplay).equals(4)
    expect(JSON.stringify(inner.state().filteredCourses)).equals(
      JSON.stringify(courses)
    )
    expect(inner.instance().renderNumberOfCatalogItems()).equals(1)
  })

  it("updates state from changeSelectedTab when selecting program tab", async () => {
    courses = [displayedCourse]
    programs = Array(5).fill(displayedProgram)
    const { inner } = await renderPage(
      {
        queries: {
          courses: {
            isPending: false,
            status:    200
          },
          programs: {
            isPending: false,
            status:    200
          }
        },
        entities: {
          courses:  courses,
          programs: programs
        }
      },
      {}
    )
    inner.instance().componentDidUpdate({}, {})
    inner.instance().changeSelectedTab("programs")
    expect(inner.state().selectedDepartment).equals("All Departments")
    expect(inner.state().tabSelected).equals("programs")
    expect(inner.state().numberCatalogRowsToDisplay).equals(4)
    expect(JSON.stringify(inner.state().filteredPrograms)).equals(
      JSON.stringify(programs)
    )
    expect(inner.instance().renderNumberOfCatalogItems()).equals(5)
  })

  it("renders catalog department filter for courses and programs without duplicates", async () => {
    const course1 = JSON.parse(JSON.stringify(displayedCourse))
    course1.departments = [{ name: "Math" }]
    const course2 = JSON.parse(JSON.stringify(displayedCourse))
    course2.departments = [{ name: "Math" }, { name: "Science" }]
    const course3 = JSON.parse(JSON.stringify(displayedCourse))
    course3.departments = [{ name: "Math" }, { name: "History" }]
    courses = [course1, course2, course3]

    const program1 = JSON.parse(JSON.stringify(displayedProgram))
    program1.departments = [{ name: "Computer Science" }, { name: "Physics" }]
    const program2 = JSON.parse(JSON.stringify(displayedProgram))
    program2.departments = []
    const program3 = JSON.parse(JSON.stringify(displayedProgram))
    program3.departments = [{ name: "Physics" }]
    programs = [program1, program2, program3]
    const { inner } = await renderPage()
    let collectedDepartments = inner
      .instance()
      .collectDepartmentsFromCatalogItems(courses)
    expect(JSON.stringify(collectedDepartments)).equals(
      JSON.stringify(["All Departments", "Math", "Science", "History"])
    )
    collectedDepartments = inner
      .instance()
      .collectDepartmentsFromCatalogItems(programs)
    expect(JSON.stringify(collectedDepartments)).equals(
      JSON.stringify(["All Departments", "Computer Science", "Physics"])
    )
  })

  it("renders catalog courses when filtered by department", async () => {
    const course1 = JSON.parse(JSON.stringify(displayedCourse))
    course1.departments = [{ name: "Math" }]
    const course2 = JSON.parse(JSON.stringify(displayedCourse))
    course2.departments = [{ name: "Science" }]
    const course3 = JSON.parse(JSON.stringify(displayedCourse))
    course3.departments = [{ name: "Science" }]
    courses = [course1, course2, course3]
    const { inner } = await renderPage()
    let coursesFilteredByCriteriaAndDepartment = inner
      .instance()
      .filteredCoursesBasedOnCourseRunCriteria("Math", courses)
    expect(coursesFilteredByCriteriaAndDepartment.length).equals(1)
    coursesFilteredByCriteriaAndDepartment = inner
      .instance()
      .filteredCoursesBasedOnCourseRunCriteria("Science", courses)
    expect(coursesFilteredByCriteriaAndDepartment.length).equals(2)
    coursesFilteredByCriteriaAndDepartment = inner
      .instance()
      .filteredCoursesBasedOnCourseRunCriteria("All Departments", courses)
    expect(coursesFilteredByCriteriaAndDepartment.length).equals(3)
  })

  it("renders no catalog courses if the course's pages are not live", async () => {
    const course = JSON.parse(JSON.stringify(displayedCourse))
    course.page.live = false
    const { inner } = await renderPage()
    const coursesFilteredByCriteriaAndDepartment = inner
      .instance()
      .filteredCoursesBasedOnCourseRunCriteria("All Departments", [course])
    expect(coursesFilteredByCriteriaAndDepartment.length).equals(0)
  })

  it("renders no catalog courses if the course has no page", async () => {
    const course = JSON.parse(JSON.stringify(displayedCourse))
    delete course.page
    const { inner } = await renderPage()
    const coursesFilteredByCriteriaAndDepartment = inner
      .instance()
      .filteredCoursesBasedOnCourseRunCriteria("All Departments", [course])
    expect(coursesFilteredByCriteriaAndDepartment.length).equals(0)
  })

  it("renders no catalog courses if the course has no associated course runs", async () => {
    const course = JSON.parse(JSON.stringify(displayedCourse))
    course.courseruns = []
    const { inner } = await renderPage()
    const coursesFilteredByCriteriaAndDepartment = inner
      .instance()
      .filteredCoursesBasedOnCourseRunCriteria("All Departments", [course])
    expect(coursesFilteredByCriteriaAndDepartment.length).equals(0)
  })

  it("renders catalog programs when filtered by department", async () => {
    const program1 = JSON.parse(JSON.stringify(displayedProgram))
    program1.departments = [{ name: "Math" }]
    const program2 = JSON.parse(JSON.stringify(displayedProgram))
    program2.departments = [{ name: "History" }]
    const program3 = JSON.parse(JSON.stringify(displayedProgram))
    program3.departments = [{ name: "History" }]
    const { inner } = await renderPage()
    programs = [program1, program2, program3]
    let programsFilteredByCriteriaAndDepartment = inner
      .instance()
      .filteredProgramsByDepartmentAndCriteria("Math", programs)
    expect(programsFilteredByCriteriaAndDepartment.length).equals(1)
    programsFilteredByCriteriaAndDepartment = inner
      .instance()
      .filteredProgramsByDepartmentAndCriteria("History", programs)
    expect(programsFilteredByCriteriaAndDepartment.length).equals(2)
    programsFilteredByCriteriaAndDepartment = inner
      .instance()
      .filteredProgramsByDepartmentAndCriteria("All Departments", programs)
    expect(programsFilteredByCriteriaAndDepartment.length).equals(3)
  })

  it("renders catalog programs only if the program is live", async () => {
    const program1 = JSON.parse(JSON.stringify(displayedProgram))
    program1.live = true
    const program2 = JSON.parse(JSON.stringify(displayedProgram))
    program2.live = true
    const { inner } = await renderPage()
    programs = [program1, program2]
    let programsFilteredByCriteriaAndDepartment = inner
      .instance()
      .filteredProgramsByDepartmentAndCriteria("All Departments", programs)
    expect(programsFilteredByCriteriaAndDepartment.length).equals(2)
    program2.live = false
    programsFilteredByCriteriaAndDepartment = inner
      .instance()
      .filteredProgramsByDepartmentAndCriteria("All Departments", programs)
    expect(programsFilteredByCriteriaAndDepartment.length).equals(1)
  })

  it("renders no catalog courses if the course's associated course run is not live", async () => {
    const courseRuns = JSON.parse(JSON.stringify(displayedCourse.courseruns))
    const { inner } = await renderPage()
    let coursesFilteredByCriteriaAndDepartment = inner
      .instance()
      .validateCoursesCourseRuns(courseRuns)
    expect(coursesFilteredByCriteriaAndDepartment.length).equals(1)
    courseRuns[0].live = false
    coursesFilteredByCriteriaAndDepartment = inner
      .instance()
      .validateCoursesCourseRuns(courseRuns)
    expect(coursesFilteredByCriteriaAndDepartment.length).equals(0)
  })

  it("renders no catalog courses if the course's associated course run has no start date", async () => {
    const courseRuns = JSON.parse(JSON.stringify(displayedCourse.courseruns))
    const { inner } = await renderPage()
    let coursesFilteredByCriteriaAndDepartment = inner
      .instance()
      .validateCoursesCourseRuns(courseRuns)
    expect(coursesFilteredByCriteriaAndDepartment.length).equals(1)
    delete courseRuns[0].start_date
    coursesFilteredByCriteriaAndDepartment = inner
      .instance()
      .validateCoursesCourseRuns(courseRuns)
    expect(coursesFilteredByCriteriaAndDepartment.length).equals(0)
  })

  it("renders no catalog courses if the course's associated course run has no enrollment start date", async () => {
    const courseRuns = JSON.parse(JSON.stringify(displayedCourse.courseruns))
    const { inner } = await renderPage()
    let coursesFilteredByCriteriaAndDepartment = inner
      .instance()
      .validateCoursesCourseRuns(courseRuns)
    expect(coursesFilteredByCriteriaAndDepartment.length).equals(1)
    delete courseRuns[0].enrollment_start
    coursesFilteredByCriteriaAndDepartment = inner
      .instance()
      .validateCoursesCourseRuns(courseRuns)
    expect(coursesFilteredByCriteriaAndDepartment.length).equals(0)
  })

  it("renders no catalog courses if the course's associated course run has an enrollment start date in the future", async () => {
    const courseRuns = JSON.parse(JSON.stringify(displayedCourse.courseruns))
    const { inner } = await renderPage()
    let coursesFilteredByCriteriaAndDepartment = inner
      .instance()
      .validateCoursesCourseRuns(courseRuns)
    expect(coursesFilteredByCriteriaAndDepartment.length).equals(1)
    courseRuns[0].enrollment_start = moment().add(2, "M")
    coursesFilteredByCriteriaAndDepartment = inner
      .instance()
      .validateCoursesCourseRuns(courseRuns)
    expect(coursesFilteredByCriteriaAndDepartment.length).equals(0)
  })

  it("renders no catalog courses if the course's associated course run has an enrollment end date in the past", async () => {
    const courseRuns = JSON.parse(JSON.stringify(displayedCourse.courseruns))
    const { inner } = await renderPage()
    let coursesFilteredByCriteriaAndDepartment = inner
      .instance()
      .validateCoursesCourseRuns(courseRuns)
    expect(coursesFilteredByCriteriaAndDepartment.length).equals(1)
    courseRuns[0].enrollment_end = moment().subtract(2, "M")
    coursesFilteredByCriteriaAndDepartment = inner
      .instance()
      .validateCoursesCourseRuns(courseRuns)
    expect(coursesFilteredByCriteriaAndDepartment.length).equals(0)
  })

  it("renders catalog courses if the course's associated course run has no enrollment end date", async () => {
    const courseRuns = JSON.parse(JSON.stringify(displayedCourse.courseruns))
    const { inner } = await renderPage()
    let coursesFilteredByCriteriaAndDepartment = inner
      .instance()
      .validateCoursesCourseRuns(courseRuns)
    expect(coursesFilteredByCriteriaAndDepartment.length).equals(1)
    delete courseRuns[0].enrollment_end
    coursesFilteredByCriteriaAndDepartment = inner
      .instance()
      .validateCoursesCourseRuns(courseRuns)
    expect(coursesFilteredByCriteriaAndDepartment.length).equals(1)
  })

  it("renders catalog courses if the course's associated course run has an enrollment end date in the future", async () => {
    const courseRuns = JSON.parse(JSON.stringify(displayedCourse.courseruns))
    const { inner } = await renderPage()
    let coursesFilteredByCriteriaAndDepartment = inner
      .instance()
      .validateCoursesCourseRuns(courseRuns)
    expect(coursesFilteredByCriteriaAndDepartment.length).equals(1)
    courseRuns[0].enrollment_end = moment().add(2, "M")
    coursesFilteredByCriteriaAndDepartment = inner
      .instance()
      .validateCoursesCourseRuns(courseRuns)
    expect(coursesFilteredByCriteriaAndDepartment.length).equals(1)
  })

  it("renders catalog courses if the course's associated course run has an enrollment start date in the past", async () => {
    const courseRuns = JSON.parse(JSON.stringify(displayedCourse.courseruns))
    const { inner } = await renderPage()
    let coursesFilteredByCriteriaAndDepartment = inner
      .instance()
      .validateCoursesCourseRuns(courseRuns)
    expect(coursesFilteredByCriteriaAndDepartment.length).equals(1)
    courseRuns[0].enrollment_start = moment().subtract(2, "M")
    coursesFilteredByCriteriaAndDepartment = inner
      .instance()
      .validateCoursesCourseRuns(courseRuns)
    expect(coursesFilteredByCriteriaAndDepartment.length).equals(1)
  })

  it("renders catalog course card with Start Anytime label if non-self paced course runs exist and all course runs start date in the past", async () => {
    const course = JSON.parse(JSON.stringify(displayedCourse))
    const { inner } = await renderPage()
    let catalogCardTagForCourse = inner
      .instance()
      .renderCatalogCardTagForCourse(course)
    expect(catalogCardTagForCourse).equals("Start Anytime")
    course.courseruns[0].start_date = moment().add(2, "M")
    catalogCardTagForCourse = inner
      .instance()
      .renderCatalogCardTagForCourse(course)
    expect(catalogCardTagForCourse).equals(
      `Start Date: ${formatPrettyDate(course.courseruns[0].start_date)}`
    )
  })

  it("renders catalog course card with start date label if non-self paced course runs exist and all course runs start in the future", async () => {
    const course = JSON.parse(JSON.stringify(displayedCourse))
    const { inner } = await renderPage()
    let catalogCardTagForCourse = inner
      .instance()
      .renderCatalogCardTagForCourse(course)
    expect(catalogCardTagForCourse).equals("Start Anytime")
    course.courseruns[0].start_date = moment().add(2, "M")
    catalogCardTagForCourse = inner
      .instance()
      .renderCatalogCardTagForCourse(course)
    expect(catalogCardTagForCourse).equals(
      `Start Date: ${formatPrettyDate(course.courseruns[0].start_date)}`
    )
  })

  it("renders catalog course card with closest future start date label if non-self paced course runs exist and a course run start date is in the future", async () => {
    const course = JSON.parse(JSON.stringify(displayedCourse))
    // Associate a second course run with the course
    course.courseruns.push(
      JSON.parse(JSON.stringify(displayedCourse.courseruns[0]))
    )
    course.courseruns.push(
      JSON.parse(JSON.stringify(displayedCourse.courseruns[0]))
    )
    course.courseruns.push(
      JSON.parse(JSON.stringify(displayedCourse.courseruns[0]))
    )
    const { inner } = await renderPage()
    let catalogCardTagForCourse = inner
      .instance()
      .renderCatalogCardTagForCourse(course)
    expect(catalogCardTagForCourse).equals("Start Anytime")

    // Update the start dates of each associated course run to be in the future.
    course.courseruns[0].start_date = moment().add(2, "M")
    course.courseruns[1].start_date = moment().add(3, "d")
    course.courseruns[2].start_date = moment().add(2, "d")
    course.courseruns[3].is_self_paced = true
    catalogCardTagForCourse = inner
      .instance()
      .renderCatalogCardTagForCourse(course)
    // Expect the closest future start date
    expect(catalogCardTagForCourse).equals(
      `Start Date: ${formatPrettyDate(course.courseruns[2].start_date)}`
    )
  })

  it("renders catalog course card with Start Anytime if only self paced course runs exist, even if start date is in the future", async () => {
    const course = JSON.parse(JSON.stringify(displayedCourse))
    const { inner } = await renderPage()
    let catalogCardTagForCourse = inner
      .instance()
      .renderCatalogCardTagForCourse(course)
    expect(catalogCardTagForCourse).equals("Start Anytime")

    course.courseruns[0].start_date = moment().add(2, "M")
    course.courseruns[0].is_self_paced = true
    catalogCardTagForCourse = inner
      .instance()
      .renderCatalogCardTagForCourse(course)
    expect(catalogCardTagForCourse).equals("Start Anytime")
  })

  it("renders catalog courses based on selected department", async () => {
    const course1 = JSON.parse(JSON.stringify(displayedCourse))
    course1.departments = [{ name: "Math" }]
    const course2 = JSON.parse(JSON.stringify(displayedCourse))
    course2.departments = [{ name: "Math" }, { name: "History" }]
    const course3 = JSON.parse(JSON.stringify(displayedCourse))
    course3.departments = [{ name: "Math" }, { name: "History" }]
    courses = [course1, course2, course3]
    const { inner } = await renderPage(
      {
        queries: {
          courses: {
            isPending: false,
            status:    200
          },
          programs: {
            isPending: false,
            status:    200
          }
        },
        entities: {
          courses:  courses,
          programs: [displayedProgram]
        }
      },
      {}
    )
    inner.instance().componentDidUpdate({}, {})
    // Default selected department is All Departments.
    expect(inner.state().selectedDepartment).equals("All Departments")
    // Default tab selected is courses.
    expect(inner.state().tabSelected).equals("courses")
    // All of the courses should be visible.
    expect(JSON.stringify(inner.state().filteredCourses)).equals(
      JSON.stringify(courses)
    )
    // Number of catalog items should match the number of visible courses.
    expect(inner.instance().renderNumberOfCatalogItems()).equals(3)

    // Select a department to filter by.
    inner.instance().changeSelectedDepartment("History", "courses")
    // Confirm the state updated to reflect the selected department.
    expect(inner.state().selectedDepartment).equals("History")
    // Confirm the number of catalog items updated to reflect the items filtered by department.
    expect(inner.instance().renderNumberOfCatalogItems()).equals(2)
    // Confirm the courses filtered are those which have a department name matching the selected department.
    expect(JSON.stringify(inner.state().filteredCourses)).equals(
      JSON.stringify([course2, course3])
    )

    // Change to the programs tab.
    inner.instance().changeSelectedTab("programs")
    // Confirm that the selected departement resets to "All Departments".
    expect(inner.state().selectedDepartment).equals("All Departments")

    // Change back to the courses tab.
    inner.instance().changeSelectedTab("courses")
    // All of the courses should be visible.
    expect(JSON.stringify(inner.state().filteredCourses)).equals(
      JSON.stringify(courses)
    )
  })
})
