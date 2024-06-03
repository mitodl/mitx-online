// @flow
import React from "react"

import { Formik, Field, Form, ErrorMessage } from "formik"

import { PasswordInput } from "./elements/inputs"
import FormError from "./elements/FormError"
import {
  resetPasswordFormValidation,
  passwordFieldErrorMessage
} from "../../lib/validation"
import CardLabel from "../input/CardLabel"
import { ConnectedFocusError } from "focus-formik-error"

type Props = {
  onSubmit: Function
}

export type ResetPasswordFormValues = {
  newPassword: string,
  confirmPassword: string
}

const ResetPasswordForm = ({ onSubmit }: Props) => (
  <Formik
    onSubmit={onSubmit}
    validationSchema={resetPasswordFormValidation}
    initialValues={{
      newPassword:   "",
      reNewPassword: ""
    }}
  >
    {({ isSubmitting, errors }) => {
      return (
        <Form noValidate>
          <ConnectedFocusError />
          <div className="form-group">
            <CardLabel
              htmlFor="newPassword"
              isRequired={true}
              label="New Password"
            />
            <Field
              name="newPassword"
              id="newPassword"
              className="form-control"
              component={PasswordInput}
              aria-invalid={errors.newPassword ? "true" : null}
              aria-describedby={errors.newPassword ? "newPasswordError" : null}
              title={passwordFieldErrorMessage}
              required
            />
            <ErrorMessage
              name="newPassword"
              id="newPasswordError"
              component={FormError}
            />
          </div>
          <div className="form-group">
            <CardLabel
              htmlFor="confirmPassword"
              isRequired={true}
              label="Confirm Password"
            />
            <Field
              name="confirmPassword"
              id="confirmPassword"
              className="form-control"
              component={PasswordInput}
              aria-invalid={errors.newPassword ? "true" : null}
              aria-describedby={
                errors.newPassword ? "confirmPasswordError" : null
              }
              required
              title={passwordFieldErrorMessage}
            />
            <ErrorMessage
              name="confirmPassword"
              id="confirmPasswordError"
              component={FormError}
            />
          </div>
          <div className="row submit-row no-gutters">
            <div className="col d-flex justify-content-end">
              <button
                type="submit"
                className="btn btn-primary btn-gradient-red-to-blue large"
                disabled={isSubmitting}
              >
                Submit
              </button>
            </div>
          </div>
        </Form>
      )
    }}
  </Formik>
)

export default ResetPasswordForm
