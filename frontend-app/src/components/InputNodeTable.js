import React, { Component } from "react";
import { PrimaryButton, Text } from "@fluentui/react";
import NodeTableTextField from "./NodeTableTextField";
import NodesContext from "./NodesContext";

class InputNodeTable extends Component {
  constructor(props) {
    super(props);

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
  }

  render() {
    return (
      <NodesContext.Consumer>
        {(context) => (
          <tbody>
            {!this.props.fixed && (
              <tr>
                <td></td>
                {this.props.data.map((_, index) => {
                  return (
                    <td key={`header_${index}`}>
                      <Text>{this.months[index % 12]}</Text>
                    </td>
                  );
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
                    {this.props.data.map((row, layerIdx) => {
                      return (
                        <td key={layerIdx}>
                          <NodeTableTextField
                            data={row[nomIdx]}
                            nodeId={this.props.nodeId}
                            layerIdx={layerIdx}
                            nomIdx={nomIdx}
                            type={"input"}
                            updateData={context.updateInputNodeData}
                          />
                        </td>
                      );
                    })}
                  </tr>
                );
              })}
            {!this.props.fixed && (
              <tr>
                <td></td>
                {this.props.data.map((_, index) => {
                  return (
                    <td key={`copy_${index}`}>
                      <PrimaryButton
                        className="table-input"
                        onClick={() => {
                          context.copyToAllLayers(this.props.nodeId, index);
                        }}
                        text="Copy to All"
                      />
                    </td>
                  );
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
