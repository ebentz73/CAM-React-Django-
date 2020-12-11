import React, { Component } from "react";

class Node extends Component {
  constructor(props) {
    super(props);
    this.state = {
      tableToggle: false,
    };
  }

  render() {
    const {
      isSelected,
      onClick,
      node: { name },
    } = this.props;

    return (
      <div className={isSelected ? "node highlight" : "node"} onClick={onClick}>
        <div className="node-header">
          <div className="node-header-label">{name}</div>
        </div>
      </div>
    );
  }
}

export default Node;
