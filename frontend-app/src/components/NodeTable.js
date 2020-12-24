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
                <div style={{ fontSize: "xx-large" }}>
                  {this.props.nodeOnChart.name}
                </div>
                <TooltipHost content={this.props.nodeOnChart.notes}>
                  <ActionButton
                    iconProps={{
                      iconName: "StatusCircleQuestionMark",
                      styles: {
                        root: {
                          fontSize: "30px",
                          border: "2px solid black",
                          borderRadius: "50%",
                          height: "24px",
                          paddingTop: "5px",
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
