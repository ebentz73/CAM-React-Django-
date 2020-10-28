import React, {Component} from "react";
import {ScrollablePane, PrimaryButton, Text} from "@fluentui/react";
import NodeTableTextField from "./NodeTableTextField";
import NodesContext from "./NodesContext";
import FixedVariableToggle from "./FixedVariableToggle";
import InputNodeTable from "./InputNodeTable";
import ConstNodeTable from "./ConstNodeTable";

class NodeTable extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            this.props.nodeId.length > 0 &&
            <React.Fragment>
                <div style={{textAlign: 'right'}} ><FixedVariableToggle /></div>
                <div className="node-table">
                    <div className="table-scroll-pane">
                        <table className="table-in-scroll-pane">
                            {this.props.type === 'input' ?
                                <InputNodeTable nodeId={this.props.nodeId} data={this.props.data} /> :
                                <ConstNodeTable nodeId={this.props.nodeId} data={this.props.data} />
                            }
                        </table>
                    </div>
                </div>
            </React.Fragment>
        );
    }
}

export default NodeTable;