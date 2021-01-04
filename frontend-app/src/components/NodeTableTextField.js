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
    this.onFocus = this.onFocus.bind(this);
  }

  componentWillReceiveProps(nextProps) {
    if (nextProps.data !== this.state.value) {
      this.setState({ value: nextProps.data });
      this.props.validate();
    }
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
        this.props.updateData(
          this.props.nodeId,
          this.props.layerIdx,
          this.props.nomIdx,
          formatted
        );
        this.props.validate();
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
    if (this.props.type === "const") {
      this.setState();
    } else {
      this.props.validate();
      if (e.key === "Enter") {
        this.props.changeFocus();
      }
    }
  }

  onFocus() {
    if (this.props.type !== "const") {
      this.props.validate();
    }
  }

  render() {
    const Styles = {
      fieldGroup: [{ backgroundColor: "lightcoral" }],
    };
    let { isShowWarning } = this.props;
    return isShowWarning ? (
      <TextField
        value={this.state.value}
        className="table-input"
        onChange={(e, val) => {
          this.setState({ value: val });
        }}
        onBlur={this.setData}
        onFocus={this.onFocus}
        onKeyPress={this.handleKeyPress}
        ref={this.props.textFieldRef}
        disabled={this.props.isReadOnly}
        errorMessage
        styles={Styles}
      />
    ) : (
      <TextField
        value={this.state.value}
        className="table-input"
        onChange={(e, val) => {
          this.setState({ value: val });
        }}
        onFocus={this.onFocus}
        onBlur={this.setData}
        onKeyPress={this.handleKeyPress}
        ref={this.props.textFieldRef}
        disabled={this.props.isReadOnly}
      />
    );
  }
}

export default NodeTableTextField;
