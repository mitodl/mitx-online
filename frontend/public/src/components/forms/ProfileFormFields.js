import React from "react"
import moment from "moment"
import { range, reverse } from "ramda"
import { ErrorMessage, Field } from "formik"
import * as yup from "yup"

import {
  EMPLOYMENT_EXPERIENCE,
  EMPLOYMENT_FUNCTION,
  EMPLOYMENT_INDUSTRY,
  EMPLOYMENT_LEVEL,
  EMPLOYMENT_SIZE,
  HIGHEST_EDUCATION_CHOICES
} from "../../constants"
import FormError from "./elements/FormError"
import CardLabel from "../input/CardLabel"

import {
  passwordField,
  usernameField,
  passwordFieldRegex,
  passwordFieldErrorMessage,
  usernameFieldRegex,
  usernameFieldErrorMessage
} from "../../lib/validation"

export const NAME_REGEX =
  "^(?![~!@&\\)\\(+:'.?,\\-]+)([^\\/\\^$#*=\\[\\]`%_;\\\\<>\\{\\}\"\\|]+)$"

const seedYear = moment().year()

// Field Error messages
export const NAME_REGEX_FAIL_MESSAGE =
  "Name cannot start with a special character (~!@&)(+:'.?,-), and cannot contain any of (/^$#*=[]`%_;\\<>{}\"|)"

export const fullNameRegex = "^.{2,255}$"
const fullNameErrorMessage = "Full name must be between 2 and 254 characters."

const countryRegex = "^\\S{2,}$"

export const legalAddressValidation = yup.object().shape({
  name: yup
    .string()
    .required()
    .label("Full Name"),
  legal_address: yup.object().shape({
    first_name: yup
      .string()
      .required()
      .label("First Name"),
    last_name: yup
      .string()
      .required()
      .label("Last Name"),
    country: yup
      .string()
      .required()
      .label("Country"),
    state: yup
      .string()
      .label("State")
      .when("country", {
        is:   value => value === "US" || value === "CA",
        then: yup
          .string()
          .required("State is a required field")
          .typeError("State is a required field"),
        otherwise: yup.string().nullable()
      })
  })
})

export const newAccountValidation = yup.object().shape({
  password: passwordField,
  username: usernameField
})

export const profileValidation = yup.object().shape({
  user_profile: yup.object().shape({
    gender: yup
      .string()
      .label("Gender")
      .nullable(),
    year_of_birth: yup
      .number()
      .min(13 - new Date().getFullYear())
      .label("Year of Birth")
      .required()
  })
})

export const addlProfileFieldsValidation = yup.object().shape({
  user_profile: yup.object().shape({
    company: yup
      .string()
      .label("Company")
      .nullable(),
    job_title: yup
      .string()
      .label("Job Title")
      .nullable(),
    industry: yup
      .string()
      .label("Industry")
      .nullable(),
    job_function: yup
      .string()
      .label("Job Function")
      .nullable(),
    company_size: yup
      .string()
      .label("Company Size")
      .nullable(),
    years_experience: yup
      .string()
      .label("Years of Work Experience")
      .nullable(),
    leadership_level: yup
      .string()
      .label("Leadership Level")
      .nullable()
  }),
  highest_education: yup
    .string()
    .label("Highest Level of Education")
    .nullable(),
  type_is_student:      yup.boolean().nullable(),
  type_is_professional: yup.boolean().nullable(),
  type_is_educator:     yup.boolean().nullable(),
  type_is_other:        yup.boolean().nullable()
})

export const requireLearnerTypeFields = {
  name:      "require_learner_type_fields",
  message:   "Please specify which category you fall into.",
  exclusive: false,
  params:    {},
  test:      (testValue: any, context: any) => {
    return (
      testValue ||
      context.parent.type_is_student ||
      context.parent.type_is_professional ||
      context.parent.type_is_educator ||
      context.parent.type_is_other
    )
  }
}

type LegalAddressProps = {
  countries: Array<Country>,
  setFieldValue: Function,
  setFieldTouched: Function,
  values: Object,
  isNewAccount: boolean
}

type AddlProfileFieldsProps = {
  values: Object,
  setFieldValue: Function,
  requireAddlFields: ?boolean
}

const findStates = (country: string, countries: Array<Country>) => {
  if (!countries) {
    return null
  }

  const foundCountry = countries.find(elem => elem.code === country)
  return foundCountry && foundCountry.states && foundCountry.states.length > 0
    ? foundCountry.states
    : null
}

const renderYearOfBirthField = errors => {
  const hasError =
    errors && errors.user_profile && errors.user_profile.year_of_birth
  return (
    <div>
      <CardLabel
        htmlFor="user_profile.year_of_birth"
        isRequired={true}
        label="Year of Birth"
      />
      <Field
        component="select"
        name="user_profile.year_of_birth"
        id="user_profile.year_of_birth"
        className="form-control"
        autoComplete="bday-year"
        aria-invalid={hasError ? "true" : null}
        aria-describedby={hasError ? "year-of-birth-error" : null}
      >
        <option value="">-----</option>
        {reverse(range(seedYear - 120, seedYear - 13)).map((year, i) => (
          <option key={i} value={year}>
            {year}
          </option>
        ))}
      </Field>
      <ErrorMessage name="user_profile.year_of_birth" component={FormError} />
    </div>
  )
}

export const LegalAddressFields = ({
  errors,
  countries,
  isNewAccount,
  values
}: LegalAddressProps) => {
  const addressErrors = errors && errors.legal_address
  return (
    <React.Fragment>
      <div className="form-group">
        <CardLabel
          htmlFor="legal_address.first_name"
          isRequired={true}
          label="First Name"
          subLabel="Name that will appear on emails"
        />
        <Field
          type="text"
          name="legal_address.first_name"
          id="legal_address.first_name"
          className="form-control"
          autoComplete="given-name"
          aria-invalid={
            addressErrors && addressErrors.first_name ? "true" : null
          }
          aria-describedby={
            addressErrors && addressErrors.first_name
              ? "first-name-error"
              : null
          }
          aria-required="true"
          aria-label="First Name"
          pattern={NAME_REGEX}
          title={NAME_REGEX_FAIL_MESSAGE}
        />
        <ErrorMessage name="legal_address.first_name" component={FormError} />
      </div>
      <div className="form-group">
        <CardLabel
          htmlFor="legal_address.last_name"
          isRequired={true}
          label="Last Name"
        />
        <Field
          type="text"
          name="legal_address.last_name"
          id="legal_address.last_name"
          className="form-control"
          autoComplete="family-name"
          aria-invalid={
            addressErrors && addressErrors.last_name ? "true" : null
          }
          aria-describedby={
            addressErrors && addressErrors.last_name ? "last-name-error" : null
          }
          pattern={NAME_REGEX}
          title={NAME_REGEX_FAIL_MESSAGE}
        />
        <ErrorMessage name="legal_address.last_name" component={FormError} />
      </div>
      <div className="form-group">
        <CardLabel
          htmlFor="name"
          isRequired={true}
          label="Full Name"
          subLabel="Name that will appear on your certificate"
        />
        <Field
          type="text"
          name="name"
          id="name"
          className="form-control"
          autoComplete="name"
          aria-invalid={errors.name ? "true" : null}
          aria-describedby={errors.name ? "full-name-error" : null}
          aria-label="Full Name"
          pattern={fullNameRegex}
          title={fullNameErrorMessage}
        />
        <ErrorMessage name="name" component={FormError} />
      </div>
      {isNewAccount ? (
        <React.Fragment>
          <div className="form-group">
            <CardLabel
              htmlFor="username"
              isRequired={true}
              label="Public Username"
              subLabel="Name that will identify you in courses"
            />
            <Field
              type="text"
              name="username"
              className="form-control"
              autoComplete="username"
              id="username"
              aria-invalid={errors.username ? "true" : null}
              aria-describedby={errors.username ? "username-error" : null}
              aria-label="Public Username"
              pattern={usernameFieldRegex}
              title={usernameFieldErrorMessage}
            />
            <ErrorMessage name="username" component={FormError} />
          </div>
          <div className="form-group">
            <CardLabel htmlFor="password" isRequired={true} label="Password" />
            <Field
              type="password"
              name="password"
              id="password"
              aria-invalid={errors.password ? "true" : null}
              aria-describedby={errors.password ? "password-error" : null}
              className="form-control"
              autoComplete="new-password"
              pattern={passwordFieldRegex}
              title={passwordFieldErrorMessage}
            />
            <ErrorMessage name="passwrod" component={FormError} />
            <div id="password-subtitle" className="label-secondary">
              Passwords must contain at least 8 characters and at least 1 number
              and 1 letter.
            </div>
          </div>
        </React.Fragment>
      ) : null}
      <div className="form-group">
        <CardLabel
          htmlFor="legal_address.country"
          isRequired={true}
          label="Country"
        />
        <Field
          component="select"
          name="legal_address.country"
          id="legal_address.country"
          aria-invalid={addressErrors && addressErrors.country ? "true" : null}
          aria-describedby={
            addressErrors && addressErrors.country ? "country-error" : null
          }
          className="form-control"
          autoComplete="country"
          pattern={countryRegex}
        >
          <option value="">-----</option>
          {countries
            ? countries.map((country, i) => (
              <option key={i} value={country.code}>
                {country.name}
              </option>
            ))
            : null}
        </Field>
        <ErrorMessage name="legal_address.country" component={FormError} />
      </div>
      {findStates(values.legal_address.country, countries) ? (
        <div className="form-group">
          <CardLabel
            htmlFor="legal_address.state"
            isRequired={true}
            label="State"
          />
          <Field
            component="select"
            name="legal_address.state"
            id="legal_address.state"
            aria-invalid={addressErrors && addressErrors.state ? "true" : null}
            aria-describedby={
              addressErrors && addressErrors.state ? "state-error" : null
            }
            className="form-control"
            autoComplete="state"
          >
            <option value="">-----</option>
            {findStates(values.legal_address.country, countries)
              ? findStates(values.legal_address.country, countries).map(
                (state, i) => (
                  <option key={i} value={state.code}>
                    {state.name}
                  </option>
                )
              )
              : null}
          </Field>
          <ErrorMessage name="legal_address.state" component={FormError} />
        </div>
      ) : null}
      {isNewAccount ? (
        <div className="form-group">{renderYearOfBirthField(errors)}</div>
      ) : null}
    </React.Fragment>
  )
}

export const ProfileFields = props => {
  return (
    <React.Fragment>
      <div className="row small-gap">
        <div className="col">
          <div className="form-group">
            <CardLabel htmlFor="user_profile.gender" label="Gender" />

            <Field
              component="select"
              name="user_profile.gender"
              id="user_profile.gender"
              className="form-control"
            >
              <option value="">-----</option>
              <option value="f">Female</option>
              <option value="m">Male</option>
              <option value="t">Transgender</option>
              <option value="nb">Non-binary/non-conforming</option>
              <option value="o">Other / Prefer not to say</option>
            </Field>
            <ErrorMessage
              name="user_profile.gender"
              id="user_profile.genderError"
              component={FormError}
            />
          </div>
        </div>
        <div className="col">
          <div className="form-group">
            {renderYearOfBirthField(props.errors)}
          </div>
        </div>
      </div>
    </React.Fragment>
  )
}

export const AddlProfileFields = ({
  values,
  requireAddlFields
}: AddlProfileFieldsProps) => (
  <React.Fragment>
    <div className="form-group">
      <div className="row">
        <div className="col">
          <CardLabel
            htmlFor="user_profile.highest_education"
            isRequired={false}
            label="Highest Level of Education"
          />
          {requireAddlFields ? <span className="required">*</span> : ""}
          <Field
            component="select"
            name="user_profile.highest_education"
            id="user_profile.highest_education"
            className="form-control"
          >
            <option value="">-----</option>
            {HIGHEST_EDUCATION_CHOICES.map((level, i) => (
              <option key={i} value={level}>
                {level}
              </option>
            ))}
          </Field>
        </div>
      </div>
    </div>
    <div className="form-group small-gap">
      <CardLabel
        htmlFor="occupation-label"
        id="occupation-label"
        isRequired={requireAddlFields}
        label="Are you a?"
      />
      <ErrorMessage
        name="user_profile.type_is_student"
        id="user_profile.type_is_student_Error"
        component={FormError}
      />
    </div>
    <div className="row small-gap profile-student-type">
      <div className="col-6">
        <div className="form-check">
          <Field
            type="checkbox"
            name="user_profile.type_is_student"
            id="user_profile.type_is_student"
            className="form-check-input"
            aria-labelledby="occupation-label student-label"
            defaultChecked={values.user_profile.type_is_student}
          />
          <label
            className="form-check-label"
            htmlFor="user_profile.type_is_student"
            id="student-label"
          >
            {" "}
            Student
          </label>
        </div>
        <div className="form-check">
          <Field
            type="checkbox"
            name="user_profile.type_is_professional"
            id="user_profile.type_is_professional"
            className="form-check-input"
            aria-labelledby="occupation-label professional-label"
            defaultChecked={values.user_profile.type_is_professional}
          />
          <label
            className="form-check-label"
            htmlFor="user_profile.type_is_professional"
            id="professional-label"
          >
            {" "}
            Professional
          </label>
        </div>
      </div>
      <div className="col-5">
        <div className="form-check">
          <Field
            type="checkbox"
            name="user_profile.type_is_educator"
            id="user_profile.type_is_educator"
            className="form-check-input"
            aria-labelledby="occupation-label educator-label"
            defaultChecked={values.user_profile.type_is_educator}
          />
          <label
            className="form-check-label"
            htmlFor="user_profile.type_is_educator"
            id="educator-label"
          >
            {" "}
            Educator
          </label>
        </div>
        <div className="form-check">
          <Field
            type="checkbox"
            name="user_profile.type_is_other"
            id="user_profile.type_is_other"
            className="form-check-input"
            aria-labelledby="occupation-label other-label"
            defaultChecked={values.user_profile.type_is_other}
          />
          <label
            className="form-check-label"
            htmlFor="user_profile.type_is_other"
            id="other-label"
          >
            {" "}
            Other
          </label>
        </div>
      </div>
    </div>
    {values.user_profile.type_is_professional ? (
      <React.Fragment>
        <Field
          type="hidden"
          name="user_profile.addl_fields_flag"
          value={true}
        />
        <div className="form-group">
          <CardLabel htmlFor="user_profile.company" label="Company" />
          <Field
            type="text"
            name="user_profile.company"
            id="user_profile.company"
            autoComplete="organization"
            aria-describedby="user_profile.companyError"
            className="form-control"
          />
          <ErrorMessage
            name="user_profile.company"
            id="user_profile.companyError"
            component={FormError}
          />
        </div>
        <div className="row small-gap">
          <div className="col">
            <div className="form-group">
              <CardLabel htmlFor="user_profile.job_title" label="Job Title" />
              <Field
                type="text"
                name="user_profile.job_title"
                id="user_profile.job_title"
                autoComplete="organization-title"
                aria-describedby="user_profile.job_title_error"
                className="form-control"
              />
              <ErrorMessage
                name="user_profile.job_title"
                id="user_profile.job_title_error"
                component={FormError}
              />
            </div>
          </div>
          <div className="col">
            <div className="form-group">
              <CardLabel
                htmlFor="user_profile.company_size"
                label="Company Size"
              />
              <Field
                component="select"
                name="user_profile.company_size"
                id="user_profile.company_size"
                className="form-control"
              >
                <option value="">-----</option>
                {EMPLOYMENT_SIZE.map(([value, label], i) => (
                  <option key={i} value={value}>
                    {label}
                  </option>
                ))}
              </Field>
            </div>
          </div>
        </div>
        <div className="row small-gap">
          <div className="col">
            <div className="form-group">
              <CardLabel htmlFor="user_profile.industry" label="Industry" />
              <Field
                component="select"
                name="user_profile.industry"
                id="user_profile.industry"
                className="form-control"
              >
                <option value="">-----</option>
                {EMPLOYMENT_INDUSTRY.map((industry, i) => (
                  <option key={i} value={industry}>
                    {industry}
                  </option>
                ))}
              </Field>
            </div>
          </div>
          <div className="col">
            <div className="form-group">
              <CardLabel
                htmlFor="user_profile.job_function"
                label="Job Function"
              />
              <Field
                component="select"
                name="user_profile.job_function"
                id="user_profile.job_function"
                className="form-control"
              >
                <option value="">-----</option>
                {EMPLOYMENT_FUNCTION.map((jobFunction, i) => (
                  <option key={i} value={jobFunction}>
                    {jobFunction}
                  </option>
                ))}
              </Field>
            </div>
          </div>
        </div>
        <div className="row small-gap">
          <div className="col">
            <div className="form-group">
              <CardLabel
                htmlFor="user_profile.years_experience"
                label="Years of Work Experience"
              />
              <Field
                component="select"
                name="user_profile.years_experience"
                id="user_profile.years_experience"
                className="form-control"
              >
                <option value="">-----</option>
                {EMPLOYMENT_EXPERIENCE.map(([value, label], i) => (
                  <option key={i} value={value}>
                    {label}
                  </option>
                ))}
              </Field>
            </div>
          </div>
          <div className="col">
            <div className="form-group">
              <CardLabel
                htmlFor="user_profile.leadership_level"
                label="Leadership Level"
              />
              <Field
                component="select"
                name="user_profile.leadership_level"
                id="user_profile.leadership_level"
                className="form-control"
              >
                <option value="">-----</option>
                {EMPLOYMENT_LEVEL.map((level, i) => (
                  <option key={i} value={level}>
                    {level}
                  </option>
                ))}
              </Field>
            </div>
          </div>
        </div>
      </React.Fragment>
    ) : null}
  </React.Fragment>
)
