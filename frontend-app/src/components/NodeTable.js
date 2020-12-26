import React, { Component } from "react";
import {
  TooltipHost,
  ActionButton,
  MessageBar,
  MessageBarType,
} from "@fluentui/react";
import FixedVariableToggle from "./FixedVariableToggle";
import InputNodeTable from "./InputNodeTable";
import ConstNodeTable from "./ConstNodeTable";

class NodeTable extends Component {
  constructor(props) {
    super(props);

    this.state = {
      fixed: false,
      errorMessage: [],
      isShowWarning: false,
    };

    this.nomLabels = ["Lower Bound", "Low", "Nominal", "High", "Upper Bound"];

    this.toggleFixedTableView = this.toggleFixedTableView.bind(this);
    this.validate = this.validate.bind(this);
    this.hideWarning = this.hideWarning.bind(this);
  }

  validate(yIndex, xIndex, newValue) {
    let errorMessage = [];
    for (let i = yIndex + 1; i < this.props.data.length; i++) {
      if (newValue > this.props.data[xIndex][i]) {
        errorMessage.push(
          `${this.nomLabels[yIndex]} must be less than or equal to ${this.nomLabels[i]}.`
        );
      }
    }
    this.setState({ errorMessage });
    if (errorMessage.length > 0) {
      this.setState({ isShowWarning: true });
      return false;
    } else {
      this.setState({ isShowWarning: false });
      return true;
    }
  }

  hideWarning() {
    this.setState({ isShowWarning: false });
  }

  toggleFixedTableView(val) {
    this.setState({ fixed: val });
  }

  render() {
    return (
      this.props.nodeId.length > 0 && (
        <React.Fragment>
          {this.state.isShowWarning && (
            <MessageBar
              messageBarType={MessageBarType.severeWarning}
              onDismiss={this.hideWarning}
              isMultiline={false}
              dismissButtonAriaLabel="Close"
            >
              {this.state.errorMessage.map((message, key) => (
                <p key={key}>{message}</p>
              ))}
            </MessageBar>
          )}
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
                    validate={this.validate}
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
