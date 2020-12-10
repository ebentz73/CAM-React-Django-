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
                                {this.props.data.flatMap((_, index) => {
                                    return index < this.props.layerOffset ? [] : [(
                                        <td key={`header_${index}`}>
                                            <Text>{this.months[index % 12]}</Text>
                                        </td>
                                    )];
                                })}
                            </tr>
                        }
                        <tr>
                            {this.props.fixed &&
                                <td key={0}><NodeTableTextField data={this.props.data[0]} nodeId={this.props.nodeId}
                                                                           layerIdx={0}
                                                                           type={'const'}
                                                                           updateData={context.updateConstNodeData}/></td>
                            }
                            {!this.props.fixed && this.props.data.flatMap((row, layerIdx) => {
                                return layerIdx < this.props.layerOffset ? [] : [(
                                    <td key={layerIdx}><NodeTableTextField data={row} nodeId={this.props.nodeId}
                                                                           layerIdx={layerIdx}
                                                                           type={'const'}
                                                                           updateData={context.updateConstNodeData}/>
                                    </td>)];
                            })}
                        </tr>
                        {!this.props.fixed &&
                            <tr>
                                {this.props.data.flatMap((_, index) => {
                                    return index < this.props.layerOffset ? [] : [(
                                        <td key={`copy_${index}`}>
                                            <PrimaryButton className="table-input"
                                                           onClick={() => {context.copyToAllLayers(this.props.nodeId, index)}}
                                                           text="Copy to All" />
                                        </td>
                                    )];
                                })}
                            </tr>
                        }
                    </tbody>
                }
            </NodesContext.Consumer>
        );
    }
}

export default ConstNodeTable;