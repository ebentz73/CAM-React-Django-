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
            this.props.data &&
            <NodesContext.Consumer>
                    {(context) =>
                        <tbody>
                            <tr>
                                {this.props.data.map((_, index) => {
                                    return (
                                        <td key={`header_${index}`}>
                                            <Text>{this.months[index % 12]}</Text>
                                        </td>
                                    );
                                })}
                            </tr>
                            <tr>
                                {this.props.data.map((row, layerIdx) => {
                                    return(<td key={layerIdx}><NodeTableTextField data={row} nodeId={this.props.nodeId}
                                                                               layerIdx={layerIdx}
                                                                               type={'input'}
                                                                               updateData={context.updateInputNodeData}/></td>);
                                })}
                            </tr>
                            <tr>
                                {this.props.data.map((_, index) => {
                                    return (
                                        <td key={`copy_${index}`}>
                                            <PrimaryButton className="table-input"
                                                           onClick={() => {context.copyToAllLayers(this.props.nodeId, index)}}
                                                           text="Copy to All" />
                                        </td>
                                    );
                                })}
                            </tr>
                        </tbody>
                    }
                </NodesContext.Consumer>
        );
    }
}

export default ConstNodeTable;