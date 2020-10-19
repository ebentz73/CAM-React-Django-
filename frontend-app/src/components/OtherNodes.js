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
            constNodes: [],
            numVisible: 0
        }

        this.tableToggle = this.tableToggle.bind(this);
    }

    componentWillReceiveProps(nextProps, nextContext) {
        if (this.props.nodes != nextProps.nodes){
            this.filterConstNodes(nextProps.nodes);
        }
    }

    filterConstNodes(nodes){
        let numVisible = 0;
        let constNodes = [];
        Object.keys(nodes).map(node_id => {
            if(nodes[node_id].type === 'const') {
                constNodes.push({...nodes[node_id], id: node_id});
                if (nodes[node_id].visible) numVisible++;
            }
        });
        this.setState({constNodes: constNodes, numVisible: numVisible});
    }

    componentDidMount() {
        this.filterConstNodes(this.props.nodes);
    }

    tableToggle() {
        this.setState({tableToggle: !this.state.tableToggle});
    }

    render() {
        return (
            (this.state.numVisible > 0) &&
            <div>
                <div className="node-header" onClick={this.tableToggle}>
                    <div className="node-header-label"><Text variant="mediumPlus">Other</Text></div>
                </div>
                {this.state.tableToggle && <OtherNodesTable constNodes={this.state.constNodes} /> }
            </div>
        )
    }
}

export default OtherNodes;