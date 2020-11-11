import React, {Component} from "react";
import {TextField} from "@fluentui/react";

class NodeTableTextField extends Component {
    constructor(props) {
        super(props);

        this.state = {
            value: props.data.toString(),
            data: props.data
        }

        this.setData = this.setData.bind(this);
        this.handleKeyPress = this.handleKeyPress.bind(this);
    }

    setData(e) {
        let val = parseFloat(this.state.value);
        if (!isNaN(val) && this.props.data !== val) {
            if (this.props.type === 'const') {
                this.props.updateData(this.props.nodeId, this.props.layerIdx, val);
            } else {
                this.props.updateData(this.props.nodeId, this.props.layerIdx, this.props.nomIdx, val);
            }
        }
    }

    handleKeyPress(e) {
        if (e.key === 'Enter') {
            this.setData();
        }
    }

    componentWillReceiveProps(nextProps, nextContext) {
        if (this.props.data !== nextProps.data) {
            this.setState({value: nextProps.data});
        }
    }

    render(){
        return (
            <TextField value={this.state.value} className="table-input"
                       onChange={(e, val) => {this.setState({value: val})}}
                       onBlur={this.setData}
                       onKeyPress={this.handleKeyPress} />
        );
    }
}

export default NodeTableTextField;