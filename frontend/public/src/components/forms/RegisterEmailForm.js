// @flow
/* global SETTINGS:false */
import React from "react"
import * as yup from "yup"

import { Formik, Field, Form, ErrorMessage } from "formik"

import ScaledRecaptcha from "../ScaledRecaptcha"
import { EmailInput } from "./elements/inputs"
import FormError from "./elements/FormError"
import { routes } from "../../lib/urls"
import { ConnectedFocusError } from "focus-formik-error"
import { emailField } from "../../lib/validation"
import CardLabel from "../input/CardLabel"

const emailValidation = yup.object().shape({
  recaptcha: SETTINGS.recaptchaKey ?
    yup.string().required("Please verify you're not a robot") :
    yup.mixed().notRequired(),
  email: emailField
})

type Props = {
  onSubmit: Function
}

export type RegisterEmailFormValues = {
  email: string,
  recaptcha: ?string
}

const RegisterEmailForm = ({ onSubmit }: Props) => (
  <Formik
    onSubmit={onSubmit}
    validationSchema={emailValidation}
    validateOnChange={false}
    validateOnBlur={false}
    initialValues={{
      email:     "",
      recaptcha: SETTINGS.recaptchaKey ? "" : undefined
    }}
  >
    {({ errors, setFieldValue, isSubmitting }) => {
      return (
        <Form noValidate>
          <ConnectedFocusError />
          <div className="form-group">
            <CardLabel htmlFor="email" isRequired={true} label="Email" />
            <Field
              name="email"
              id="email"
              className="form-control"
              autoComplete="email"
              component={EmailInput}
              aria-invalid={errors.email ? "true" : null}
              aria-describedby={errors.email ? "emailError" : null}
              required
            />
            <ErrorMessage name="email" id="emailError" component={FormError} />
            <p>
              By creating an account I agree to the
              <br />
              <a
                href={routes.informationLinks.honorCode}
                target="_blank"
                rel="noopener noreferrer"
              >
                Honor Code
              </a>
              {", "}
              <a
                href={routes.informationLinks.termsOfService}
                target="_blank"
                rel="noopener noreferrer"
              >
                Terms of Service
              </a>
              {" and "}
              <a
                href={routes.informationLinks.privacyPolicy}
                target="_blank"
                rel="noopener noreferrer"
              >
                Privacy Policy
              </a>
              {"."}
            </p>
          </div>
          {SETTINGS.recaptchaKey ? (
            <div className="form-group">
              <ScaledRecaptcha
                onRecaptcha={value => setFieldValue("recaptcha", value)}
                recaptchaKey={SETTINGS.recaptchaKey}
              />
              <ErrorMessage name="recaptcha" component={FormError} />
            </div>
          ) : null}
          <button
            type="submit"
            className="btn btn-primary btn-gradient-red-to-blue large"
            disabled={isSubmitting}
          >
            Continue
          </button>
        </Form>
      )
    }}
  </Formik>
)

export default RegisterEmailForm
