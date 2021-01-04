import React, { Component } from "react";

class FixedVariableToggle extends Component {
  constructor(props) {
    super(props);

    this.state = {
      variable: !props.fixed,
    };

    this.toggleVariable = this.toggleVariable.bind(this);
  }

  componentDidUpdate(prevProps, prevState, snapshot) {
    if (prevProps.fixed !== this.props.fixed) {
      this.setState({ variable: !this.props.fixed });
    }
  }

  toggleVariable(val) {
    this.setState({ variable: val });
    this.props.toggleFixed(!val);
  }

  render() {
    let leftSideStyle = {
      position: "relative",
      borderStyle: "solid",
      borderColor: this.state.variable ? "gray" : "black",
      borderWidth: this.state.variable ? "1px 0 1px 1px" : "2px",
      borderRadius: "4px 0 0 4px",
      width: "70px",
      height: "30px",
      marginBottom: !this.state.variable ? "-1px" : "0",
      marginLeft: "auto",
      display: "inline-block",
      fontFamily: "Segoe UI",
      textAlign: "center",
    };

    let leftSpanStyle = {
      position: "absolute",
      bottom: "8px",
      left: "20px",
      fontSize: "0.8em",
      color: this.state.variable ? "gray" : "black",
      userSelect: "none",
    };

    let rightSideStyle = {
      position: "relative",
      borderStyle: "solid",
      borderColor: !this.state.variable ? "gray" : "black",
      borderWidth: !this.state.variable ? "1px 1px 1px 0" : "2px",
      borderRadius: "0 4px 4px 0",
      width: "70px",
      height: "30px",
      marginLeft: "auto",
      marginBottom: this.state.variable ? "-1px" : "0",
      display: "inline-block",
      fontFamily: "Segoe UI",
      textAlign: "center",
      userSelect: "none",
    };

    let rightSpanStyle = {
      position: "absolute",
      bottom: "8px",
      left: "12px",
      fontSize: "0.8em",
      color: this.state.variable ? "black" : "gray",
    };

    return (
      <div>
        <div style={leftSideStyle} onClick={() => this.toggleVariable(false)}>
          <span style={leftSpanStyle}>Fixed</span>
        </div>
        <div style={rightSideStyle} onClick={() => this.toggleVariable(true)}>
          <span style={rightSpanStyle}>Variable</span>
        </div>
      </div>
    );
  }
}

export default FixedVariableToggle;
