import React, {Component} from "react";
import {Text} from '@fluentui/react';
import {TextField} from '@fluentui/react';
import InputNodeTable from "./InputNodeTable";
import ConstNodeTable from "./ConstNodeTable";

class Node extends Component {
    constructor(props) {
        super(props);
        this.state = {
            tableToggle: false
        }

        this.tableToggle = this.tableToggle.bind(this);
    }

    tableToggle() {
        this.setState({tableToggle: !this.state.tableToggle});
    }

    render() {
        return (
            <div>
                <div className="node-header" onClick={this.tableToggle}>
                    <div className="label"><Text variant="mediumPlus">{this.props.node.name}</Text></div>
                </div>
                {this.state.tableToggle && this.props.node.type === 'input' &&
                    <InputNodeTable nodeId={this.props.nodeId} data={this.props.node.data} />
                }
            </div>
        )
    }
}

export default Node;