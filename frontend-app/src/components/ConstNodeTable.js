import React, { Component } from "react";
import { TooltipHost, ActionButton, Text } from "@fluentui/react";
import NodeTableTextField from "./NodeTableTextField";
import NodesContext from "./NodesContext";

class ConstNodeTable extends Component {
  constructor(props) {
    super(props);
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

  render() {
    return (
      <NodesContext.Consumer>
        {(context) => {
          let constantNodes = this.props.constantNodes;
          constantNodes.sort((a, b) => {
            if (context.nodes[a].name < context.nodes[b].name) {
              return -1;
            }
            if (context.nodes[a].name > context.nodes[b].name) {
              return 1;
            }
            return 0;
          });
          return (
            <tbody>
              {!this.props.fixed && (
                <tr>
                  <td></td>
                  {context.nodes[constantNodes[0]].data.flatMap((_, index) => {
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
              {constantNodes.map((node, nodeIdx) => {
                return this.props.fixed ? (
                  <tr key={`row_${nodeIdx}`}>
                    <td>
                      <Text>{context.nodes[node].name}</Text>
                      <TooltipHost content={context.nodes[node].notes}>
                        <ActionButton
                          iconProps={{
                            iconName: "StatusCircleQuestionMark",
                            styles: {
                              root: {
                                fontSize: "20px",
                                border: "2px solid black",
                                borderRadius: "50%",
                                height: "20px",
                              },
                            },
                          }}
                        ></ActionButton>
                      </TooltipHost>
                    </td>
                    <td key={0}>
                      <NodeTableTextField
                        data={context.nodes[node].data[0]}
                        nodeId={node}
                        layerIdx={0}
                        type={"const"}
                        updateData={context.updateConstNodeData}
                      />
                    </td>
                  </tr>
                ) : (
                  <tr key={`row_${nodeIdx}`}>
                    <td className="constant-node-name">
                      <Text>{context.nodes[node].name}</Text>
                      <TooltipHost content={context.nodes[node].notes}>
                        <ActionButton
                          iconProps={{
                            iconName: "StatusCircleQuestionMark",
                            styles: {
                              root: {
                                fontSize: "20px",
                                border: "2px solid black",
                                borderRadius: "50%",
                                height: "20px",
                              },
                            },
                          }}
                        ></ActionButton>
                      </TooltipHost>
                    </td>
                    {context.nodes[node].data.flatMap((row, layerIdx) => {
                      return layerIdx < this.props.layerOffset
                        ? []
                        : [
                            <td key={layerIdx}>
                              <NodeTableTextField
                                data={row}
                                nodeId={constantNodes[layerIdx]}
                                layerIdx={layerIdx}
                                type={"const"}
                                updateData={context.updateConstNodeData}
                              />
                            </td>,
                          ];
                    })}
                  </tr>
                );
              })}
            </tbody>
          );
        }}
      </NodesContext.Consumer>
    );
  }
}

export default ConstNodeTable;
