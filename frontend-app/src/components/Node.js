import React, {Component} from "react";
import {Text, ITextProps, Icon} from '@fluentui/react';
import {ChevronUpIcon, ChevronDownIcon} from '@fluentui/react-icons'
import {PrimaryButton} from '@fluentui/react';
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
                    <div className="node-header-label">{this.props.node.name}</div>
                    <PrimaryButton text="Show on chart" style={{float: 'right'}}
                                   onClick={(e) => this.props.changeChartData(e, this.props.nodeId)} />
                    {this.state.tableToggle ?
                        <ChevronUpIcon className="node-header-chevron" /> :
                        <ChevronDownIcon className="node-header-chevron" />}
                </div>
                {this.state.tableToggle && this.props.node.type === 'input' &&
                    <InputNodeTable nodeId={this.props.nodeId} data={this.props.node.data} />
                }
            </div>
        )
    }
}

export default Node;