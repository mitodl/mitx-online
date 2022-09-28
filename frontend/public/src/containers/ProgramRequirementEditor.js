import { useState } from "react"
import {
    Tree,
    getBackendOptions,
    MultiBackend,
} from "@minoru/react-dnd-treeview"
import { NodeModel } from "@minoru/react-dnd-treeview/dist/types"
import { DndProvider } from "react-dnd"
import {isNil} from "ramda"

type Course = {
    id: number,
    title: string
}

type NodeData = {
    course: number | null,
    operator: string | null,
    operator_value: string | null,
    title: string | null
}

type TreebeardNode = {
    data: NodeData,
    children?: Array<TreebeardNode>
}

type Props = {
    value: string,
    fieldName: string,
    courses: Course[],
}

type TreebeardState = TreebeardNode[]
type TreeNode =  NodeModel<NodeData>

const getTitle = (courses: Course[], node: TreebeardNode) => {
    if (!isNil(node.operator)) {
        return node.operator
    } else {

    }
}

const fromTreebeard = (courses: Course[], tree: TreebeardState): TreeState => {
    const result: TreeState = new Array()
    let idx = 0

    const _from = (node: TreebeardNode, parentId: number) => {
        results.push({
            id: idx++,
            parentId: parentId,
            title: getTitle(courses, node.data),
            data: node.data,
        })
    }

    // walk the root nodes, using 0 since they're top level
    tree.map((child) => _from(child, 0))


    return result
}

const toTreebeard = (tree: TreeState): TreebeardState => {
    return tree
}


export default function ProgramRequirementEditor({ courses, name, value }: Props) {
    courses = JSON.parse(courses)
    value = JSON.parse(value)

    const initialTree = flattenAndMapTree(courses, value)
    const [treeData, setTreeData] = useState<TreeState>(initialTree)
    const handleDrop = (newTreeData) => setTreeData(newTreeData)

    return (
        <DndProvider backend={MultiBackend} options={getBackendOptions()}>
            <input type="hidden" name={name} value={toTreebeard(treeData)} />
            <Tree
                tree={treeData}
                rootId={0}
                onDrop={handleDrop}
                render={(node, { depth, isOpen, onToggle }) => (
                    <div style={{ marginLeft: depth * 10 }}>
                        {node.droppable && (
                            <span onClick={onToggle}>{isOpen ? "[-]" : "[+]"}</span>
                        )}
                        {node.text}
                    </div>
                )}
            />
        </DndProvider>
    )
}