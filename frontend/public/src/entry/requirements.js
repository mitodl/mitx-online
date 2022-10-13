import "core-js/stable"
import "regenerator-runtime/runtime"
import React from "react"
import ReactDOM from "react-dom"

import * as Sentry from "@sentry/browser"
// Object.entries polyfill
import entries from "object.entries"

import ProgramRequirementEditor from "../containers/ProgramRequirementEditor"

Sentry.init({
    dsn: SETTINGS.sentry_dsn,
    release: SETTINGS.release_version,
    environment: SETTINGS.environment
})

if (!Object.entries) {
    entries.shim()
}

const elements = document.querySelectorAll('#all_requirements-0 .program-requirements-field');

for (const element of elements) {
    ReactDOM.render(
        <ProgramRequirementEditor {...element.dataset} />,
        element
    )
}