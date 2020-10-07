import React, {Component} from "react";
import {Text} from '@fluentui/react';

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
                    <div className="label">{this.props.node.name}</div>
                    <div className="changes-toggle">Changes</div>
                </div>
                {this.state.tableToggle &&
                <div className="node-table">
                    <table>
                        <tbody>
                        {this.props.node.type === 'input' && this.props.node.data[0].map((_, colIndex) => {
                            return (
                                <tr key={colIndex}>
                                    {this.props.node.data.map((row, index) => {
                                        return(<td key={index}>{row[colIndex]}</td>);
                                    })}
                                </tr>
                            );
                        })}
                        {this.props.node.type === 'const' &&
                            <tr>
                                {this.props.node.data.map((val, index) => {
                                    return (<td key={{index}}>{val}</td>);
                                })}
                            </tr>
                        }
                        </tbody>
                    </table>
                </div>
                }
            </div>
        )
    }
}

export default Node;