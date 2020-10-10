import React, {Component} from "react";
import {Text} from '@fluentui/react';
import {TextField} from '@fluentui/react';
import InputNodeTable from "./InputNodeTable";
import ConstNodeTable from "./ConstNodeTable";
import OtherNodesTable from "./OtherNodesTable";

class OtherNodes extends Component {
    constructor(props) {
        super(props);
        this.state = {
            tableToggle: false,
            constNodes: []
        }

        this.tableToggle = this.tableToggle.bind(this);
    }

    componentDidMount() {
        let constNodes = [];
        Object.keys(this.props.nodes).map(node_id => {
            if(this.props.nodes[node_id].type === 'const') {
                constNodes.push({...this.props.nodes[node_id], id: node_id});
            }
        });
        this.setState({constNodes: constNodes});
    }

    tableToggle() {
        this.setState({tableToggle: !this.state.tableToggle});
    }

    render() {
        return (
            <div>
                <div className="node-header" onClick={this.tableToggle}>
                    <div className="label"><Text variant="mediumPlus">Other</Text></div>
                </div>
                {this.state.tableToggle && <OtherNodesTable constNodes={this.state.constNodes} /> }
            </div>
        )
    }
}

export default OtherNodes;