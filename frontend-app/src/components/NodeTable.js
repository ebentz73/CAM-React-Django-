import React, { Component } from "react";
import { TooltipHost, ActionButton } from "@fluentui/react";
import FixedVariableToggle from "./FixedVariableToggle";
import InputNodeTable from "./InputNodeTable";
import ConstNodeTable from "./ConstNodeTable";

class NodeTable extends Component {
  constructor(props) {
    super(props);

    this.state = {
      fixed: false,
    };

    this.toggleFixedTableView = this.toggleFixedTableView.bind(this);
  }

  toggleFixedTableView(val) {
    this.setState({ fixed: val });
  }

  render() {
    return (
      this.props.nodeId.length > 0 && (
        <React.Fragment>
          <div
            style={
              this.props.type === "input"
                ? { display: "flex", justifyContent: "space-between" }
                : { textAlign: "right" }
            }
          >
            {this.props.type === "input" && (
              <div style={{ display: "flex" }}>
                <span
                  style={{
                    fontSize: "x-large",
                    display: "flex",
                    alignItems: "center",
                  }}
                >
                  {this.props.nodeOnChart.name}
                </span>
                <TooltipHost content={this.props.nodeOnChart.notes}>
                  <ActionButton
                    iconProps={{
                      iconName: "info",
                      styles: {
                        root: {
                          fontSize: "20px",
                        },
                      },
                    }}
                  ></ActionButton>
                </TooltipHost>
              </div>
            )}
            <FixedVariableToggle toggleFixed={this.toggleFixedTableView} />
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
                    isReadOnly={this.props.isReadOnly}
                  />
                ) : (
                  <ConstNodeTable
                    nodeId={this.props.nodeId}
                    data={this.props.data}
                    fixed={this.state.fixed}
                    layerOffset={this.props.layerOffset}
                    constantNodes={this.props.constantNodes}
                    isReadOnly={this.props.isReadOnly}
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
