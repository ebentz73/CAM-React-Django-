import React, { Component } from "react";
import { PrimaryButton, Text } from "@fluentui/react";
import NodeTableTextField from "./NodeTableTextField";
import NodesContext from "./NodesContext";
import { LineThicknessIcon } from "@fluentui/react-icons";

class InputNodeTable extends Component {
  constructor(props) {
    super(props);

    this.state = {
      warningX: null,
      warningY: null,
    };

    this.nomLabels = ["Lower Bound", "Low", "Nominal", "High", "Upper Bound"];
    this.months = [
      "Jan",
      "Feb",
      "Mar",
      "Apr",
      "May",
      "Jun",
      "Jul",
      "Aug",
      "Sep",
      "Oct",
      "Nov",
      "Dec",
    ];
    this.changeFocus = this.changeFocus.bind(this);
    this.validate = this.validate.bind(this);
    this.props.data.forEach((row, yIndex) => {
      row.forEach((_, xIndex) => {
        this[`tableData${yIndex}${xIndex}`] = React.createRef();
      });
    });
  }

  formatDate(date, increment, index) {
    if (date === "") return date;
    if (increment == "day") {
      date = new Date(
        date.getFullYear(),
        date.getMonth(),
        date.getDate() + index
      );
    } else if (increment == "week") {
      date = new Date(
        date.getFullYear(),
        date.getMonth(),
        date.getDate() + 7 * index
      );
    } else if (increment == "month") {
      date = new Date(date.getFullYear(), date.getMonth() + index, 1);
    } else if (increment == "year") {
      date = new Date(date.getFullYear() + index, 1, 1);
    }
    let year = date.getFullYear();
    let month = `${date.getMonth() + 1}`.padStart(2, "0");
    let day = `${date.getDate()}`.padStart(2, "0");
    return increment === "year"
      ? `${year}`
      : increment === "month"
      ? `${year}-${month}`
      : `${year}-${month}-${day}`;
  }

  changeFocus(yIndex, xIndex) {
    if (yIndex < this.props.data.length - 1) {
      this[`tableData${yIndex + 1}${xIndex}`].focus();
    }
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
    if (errorMessage.length > 0) {
      this.setState({ warningX: xIndex, warningY: yIndex });
      this.props.showWarning(errorMessage);
      return false;
    } else {
      this.setState({ warningX: null, warningY: null });
      this.props.showWarning(null);
      return true;
    }
  }

  render() {
    return (
      <NodesContext.Consumer>
        {(context) => (
          <tbody>
            {!this.props.fixed && (
              <tr>
                <td></td>
                {this.props.data.flatMap((_, index) => {
                  return index < this.props.layerOffset
                    ? []
                    : [
                        <td key={`header_${index}`}>
                          <Text>
                            {this.formatDate(
                              context.layerStartDate,
                              context.layerTimeIncrement,
                              index
                            )}
                          </Text>
                        </td>,
                      ];
                })}
              </tr>
            )}
            {this.props.fixed &&
              this.props.data[0].map((_, nomIdx) => {
                return (
                  <tr key={nomIdx}>
                    <td>
                      <Text>{this.nomLabels[nomIdx]}</Text>
                    </td>
                    <td>
                      <NodeTableTextField
                        data={this.props.data[0][nomIdx]}
                        nodeId={this.props.nodeId}
                        layerIdx={0}
                        nomIdx={nomIdx}
                        type={"input"}
                        updateData={context.updateInputRowData}
                        isReadOnly={this.props.isReadOnly}
                        textFieldRef={(ref) =>
                          (this[`tableData${nomIdx}${layerIdx}`] = ref)
                        }
                        changeFocus={() => this.changeFocus(nomIdx, layerIdx)}
                        validate={(newValue) =>
                          this.validate(nomIdx, layerIdx, newValue)
                        }
                        isShowWarning={
                          this.state.warningX === layerIdx &&
                          this.state.warningY === nomIdx
                        }
                      />
                    </td>
                  </tr>
                );
              })}
            {!this.props.fixed &&
              this.props.data[0].map((_, nomIdx) => {
                return (
                  <tr key={nomIdx}>
                    <td>
                      <Text>{this.nomLabels[nomIdx]}</Text>
                    </td>
                    {this.props.data.flatMap((row, layerIdx) => {
                      return layerIdx < this.props.layerOffset
                        ? []
                        : [
                            <td key={layerIdx}>
                              <NodeTableTextField
                                data={row[nomIdx]}
                                nodeId={this.props.nodeId}
                                layerIdx={layerIdx}
                                nomIdx={nomIdx}
                                type={"input"}
                                updateData={context.updateInputNodeData}
                                isReadOnly={this.props.isReadOnly}
                                textFieldRef={(ref) =>
                                  (this[`tableData${nomIdx}${layerIdx}`] = ref)
                                }
                                changeFocus={() =>
                                  this.changeFocus(nomIdx, layerIdx)
                                }
                                validate={(newValue) =>
                                  this.validate(nomIdx, layerIdx, newValue)
                                }
                                isShowWarning={
                                  this.state.warningX === layerIdx &&
                                  this.state.warningY === nomIdx
                                }
                              />
                            </td>,
                          ];
                    })}
                  </tr>
                );
              })}
            {!this.props.fixed && (
              <tr>
                <td></td>
                {this.props.data.flatMap((_, index) => {
                  return index < this.props.layerOffset
                    ? []
                    : [
                        <td key={`copy_${index}`}>
                          <PrimaryButton
                            className="table-input"
                            onClick={() => {
                              context.copyToAllLayers(this.props.nodeId, index);
                            }}
                            text="Copy to All"
                            disabled={this.props.isReadOnly}
                          />
                        </td>,
                      ];
                })}
              </tr>
            )}
          </tbody>
        )}
      </NodesContext.Consumer>
    );
  }
}

export default InputNodeTable;
