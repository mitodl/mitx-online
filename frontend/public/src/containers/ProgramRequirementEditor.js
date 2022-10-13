import React from "react"
import RequirementsEditor from "../components/requirements/RequirementsEditor"


type Props = {
    items: string,
    name: string,
    courses: string,
}


export default function ProgramRequirementEditor({ courses, name, items }: Props) {
    courses = JSON.parse(courses)
    value = JSON.parse(value)

    return <RequirementsEditor name={name} courses={courses} items={items}/>
}