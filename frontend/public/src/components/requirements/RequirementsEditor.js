
import React, { useCallback, useState } from "react"

const OPERATOR_ALL_OF = "ALL_OF"
const OPERATOR_MIN_NUMBER_OF = "MIN_NUMBER_OF"

type Node = {
  id?: Number,
  data: {
    title: string,
    operator: string,
    operator_value: string,
  },
  children?: Array<Node>
}

type Course = {
  id: number,
  title: string
}

type Props = {
    items: Array<Node>,
    name: string,
    courses: Course[],
}

type OperatorProps = {
  node: Node
}


const Operator = ({node}: OperatorProps) => {
  return (
    <div>
      <input type="text" value={node.data.title} />
      <select value={node.data.operator}>
        <option value={OPERATOR_ALL_OF}>All Of</option>
        <option value={OPERATOR_MIN_NUMBER_OF}>Minimum Number Of</option>
      </select>
      {node.operator === OPERATOR_MIN_NUMBER_OF && (
        <input type="number" value={node.data.operator_value}/>
      )}
    </div>
  )
}

const operatorDefaultValue = (operator: string): string => operator === OPERATOR_MIN_NUMBER_OF ? "" : null

const addOperator = (nodes: Array<Node>, operator: string): Array<Node> => (
  [
    ...nodes,
    {
      data: {
        title: "",
        operator,
        operator_value: operatorDefaultValue(operator),
      },
      children: [],
    }
  ]
)

export default function RequirementsEditor({courses, name, items}) {
    const [nodes, setNodes] = useState<Array<Node>>(items);

    const add = useCallback(
      () => {
        setNodes(addOperator(nodes, OPERATOR_ALL_OF))
      },
      [nodes, setNodes],
    )
    
    return <>
      <input type="hidden" name={name} value={JSON.stringify(nodes)}/>
      <div>
        {nodes.forEach((node, index) => (
          <Operator node={node} key={index} />
        ))}
        <button onClick={add}>+</button>
      </div>
    </>;
}