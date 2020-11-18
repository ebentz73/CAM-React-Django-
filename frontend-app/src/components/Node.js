import React, {Component} from "react";

class Node extends Component {
    constructor(props) {
        super(props);
        this.state = {
            tableToggle: false
        }
    }

    render() {
        return (
            <div className="node" onClick={this.props.onClick}>
                <div className="node-header">
                    <div className="node-header-label">{this.props.node.name}</div>
                </div>
            </div>
        );
    }
}

export default Node;