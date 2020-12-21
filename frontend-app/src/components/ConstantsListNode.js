import React, { Component } from "react";

class ConstantsListNode extends Component {
  constructor(props) {
    super(props);
    this.state = {
        tableToggle: false,
        isSelected: false

    };

    this.onClick = this.onClick.bind(this);
  }

  onClick() {
      this.setState({isSelected: !this.state.isSelected});
  }

  render() {
      const {
          isSelected,
          onClick,
        } = this.props;
    return (
        this.props.constantNodes.length > 0 &&
        <div className={isSelected ? "node highlight" : "node"} onClick={onClick}>
          <div className="node-header">
            <div className="node-header-label">Constants</div>
          </div>
        </div>
    );
  }
}

export default ConstantsListNode;
