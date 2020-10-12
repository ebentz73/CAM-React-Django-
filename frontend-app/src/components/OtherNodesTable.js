import React, {Component} from "react";
import {ScrollablePane, Text} from "@fluentui/react";
import NodesContext from "./NodesContext";
import NodeTableTextField from "./NodeTableTextField";

class OtherNodesTable extends Component {
    constructor(props) {
        super(props);
        this.state = {
            constNodes: props.constNodes
        }

        this.updateData = this.updateData.bind(this);
    }

    updateData(node_idx, data_idx, val){
        let parsedVal = parseFloat(val);
        if (parsedVal !== NaN) {
            let newNodes = this.state.constNodes.slice();
            newNodes[node_idx].data[data_idx] = parsedVal;
            this.setState({constNodes: newNodes});
        }
    }

    render() {
        return (
            <NodesContext.Consumer>
                {(context) =>
                    <div className="node-table">
                        <ScrollablePane className="scroll-pane">
                            <table>
                                <tbody>
                                    {this.state.constNodes.map((node, colIndex) => {
                                        return (
                                            <tr key={colIndex}>
                                                <td><Text>{node.name}</Text></td>
                                                {node.data.map((data, index) => {
                                                    return(<td key={index}><NodeTableTextField data={data}
                                                                                               nodeId={node.id}
                                                                                               layerIdx={index}
                                                                                               type={'const'}
                                                                                               updateData={context.updateConstNodeData}/></td>);
                                                })}
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        </ScrollablePane>
                    </div>
                }
            </NodesContext.Consumer>
        );
    }
}

export default OtherNodesTable;