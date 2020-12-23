import React, { Component } from "react";
import FixedVariableToggle from "./FixedVariableToggle";
import InputNodeTable from "./InputNodeTable";
import ConstNodeTable from "./ConstNodeTable";

class NodeTable extends Component {
  constructor(props) {
    super(props);

    this.state = {
      fixed: props.type === "const",
    };

    this.toggleFixedTableView = this.toggleFixedTableView.bind(this);
  }

  componentDidUpdate(prevProps, prevState, snapshot) {
      if(prevProps.type !== this.props.type) {
          this.setState({fixed: this.props.type === "const"});
      }
  }

    toggleFixedTableView(val) {
    this.setState({ fixed: val });
  }

  render() {
    return (
      this.props.nodeId.length > 0 && (
        <React.Fragment>
          <div style={{ textAlign: "right" }}>
            <FixedVariableToggle fixed={this.state.fixed} toggleFixed={this.toggleFixedTableView} />
          </div>
          <div className="node-table">
            <div className="table-scroll-pane">
              <table className="table-in-scroll-pane">
                {this.props.type === "input" ? (
                  <InputNodeTable
                    nodeId={this.props.nodeId}
                    data={this.props.data}
                    fixed={this.state.fixed}
                    layerOffset={this.props.layerOffset}
                  />
                ) : (
                  <ConstNodeTable
                    nodeId={this.props.nodeId}
                    data={this.props.data}
                    fixed={this.state.fixed}
                    layerOffset={this.props.layerOffset}
                    constantNodes={this.props.constantNodes} 
                  />
                )}
              </table>
            </div>
          </div>
        </React.Fragment>
      )
    );
  }
}

export default NodeTable;
