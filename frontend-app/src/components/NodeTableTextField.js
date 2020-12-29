import React, { Component } from "react";
import { TextField } from "@fluentui/react";

class NodeTableTextField extends Component {
  constructor(props) {
    super(props);

    this.state = {
      value: this.formatFloat(parseFloat(props.data)),
      data: props.data,
    };

    this.setData = this.setData.bind(this);
    this.handleKeyPress = this.handleKeyPress.bind(this);
  }

  setData(e) {
    let val = parseFloat(this.state.value);
    if (!isNaN(val) && this.props.data !== val) {
      let formatted = this.formatFloat(val);
      if (this.props.type === "const") {
        this.props.updateData(
          this.props.nodeId,
          this.props.layerIdx,
          formatted
        );
      } else {
        if (this.props.validate(val)) {
          this.props.updateData(
            this.props.nodeId,
            this.props.layerIdx,
            this.props.nomIdx,
            formatted
          );
        }
      }
      this.state.value = formatted;
    }
  }

  formatFloat(val) {
    let formattedValue = val.toFixed(2);
    if (formattedValue.endsWith(".00")) {
      formattedValue = val.toFixed();
    }
    return formattedValue;
  }

  handleKeyPress(e) {
    if (e.key === "Enter") {
      this.setData();
      this.props.changeFocus();
    }
  }

  componentWillReceiveProps(nextProps, nextContext) {
    if (this.props.data !== nextProps.data) {
      this.setState({ value: nextProps.data });
    }
  }

  render() {
    let { isShowWarning } = this.props;
    return isShowWarning ? (
      <TextField
        value={this.state.value}
        className="table-input"
        onChange={(e, val) => {
          this.setState({ value: val });
        }}
        onBlur={this.setData}
        onKeyPress={this.handleKeyPress}
        ref={this.props.textFieldRef}
        disabled={this.props.isReadOnly}
        errorMessage
      />
    ) : (
      <TextField
        value={this.state.value}
        className="table-input"
        onChange={(e, val) => {
          this.setState({ value: val });
        }}
        onBlur={this.setData}
        onKeyPress={this.handleKeyPress}
        ref={this.props.textFieldRef}
        disabled={this.props.isReadOnly}
      />
    );
  }
}

export default NodeTableTextField;
