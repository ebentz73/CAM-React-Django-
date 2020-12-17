import React, {Component} from "react";
import {PrimaryButton, Text} from "@fluentui/react";
import NodeTableTextField from "./NodeTableTextField";
import NodesContext from "./NodesContext";

class ConstNodeTable extends Component {
    constructor(props) {
        super(props);
        this.months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    }

    render() {
        return (
            <NodesContext.Consumer>
                {(context) =>
                    <tbody>
                        {!this.props.fixed &&
                            <tr>
                                <td></td>
                                {context.nodes[this.props.constantNodes[0]].data.map((_, index) => {
                                    return (
                                        <td key={`header_${index}`}>
                                            <Text>{this.months[index % 12]}</Text>
                                        </td>
                                    );
                                })}
                            </tr>
                        }
                        {this.props.constantNodes.map((node, nodeIdx) => {
                            return(
                                this.props.fixed ?
                                    <tr key={`row_${nodeIdx}`}>
                                        <td><Text>{context.nodes[this.props.constantNodes[nodeIdx]].name}</Text></td>
                                        <td key={0}><NodeTableTextField data={context.nodes[this.props.constantNodes[nodeIdx]].data[0]}
                                                                        nodeId={this.props.constantNodes[nodeIdx]}
                                                                                   layerIdx={0}
                                                                                   type={'const'}
                                                                                   updateData={context.updateConstNodeData}/></td>
                                    </tr>

                                :
                                    <tr key={`row_${nodeIdx}`}>
                                        <td><Text>{context.nodes[this.props.constantNodes[nodeIdx]].name}</Text></td>
                                        { context.nodes[this.props.constantNodes[nodeIdx]].data.map((row, layerIdx) => {
                                        return(<td key={layerIdx}><NodeTableTextField data={row} nodeId={this.props.constantNodes[layerIdx]}
                                                                                   layerIdx={layerIdx}
                                                                                   type={'const'}
                                                                                   updateData={context.updateConstNodeData}/></td>);

                                        })}
                                    </tr>
                            );
                        })}
                    </tbody>
                }
            </NodesContext.Consumer>
        );
    }
}

export default ConstNodeTable;