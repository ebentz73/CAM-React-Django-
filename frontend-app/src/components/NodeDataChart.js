import React, { Component } from "react";
import { Line } from "react-chartjs-2";
import NodesContext from "./NodesContext";

class NodeDataChart extends Component {
  constructor(props) {
    super(props);

    this.state = {
      chartData: {
        labels: [],
        datasets: [],
      },
    };

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
          date = new Date(date.getFullYear(), date.getMonth(), date.getDate() + index);
      } else if (increment == "week") {
          date = new Date(date.getFullYear(), date.getMonth(), date.getDate() + 7 * index);
      } else if (increment == "month") {
          date = new Date(date.getFullYear(), date.getMonth() + index, 1);
      } else if (increment == "year") {
          date = new Date(date.getFullYear() + index, 1, 1);
      }
      let year = date.getFullYear();
      let month = `${date.getMonth() + 1}`.padStart(2, "0");
      let day = `${date.getDate()}`.padStart(2, "0");
      return increment === "year" ? `${year}` : increment === "month" ? `${year}-${month}` : `${year}-${month}-${day}`;
  }

  setupChartData(node) {
    if (node !== undefined && node.data !== undefined) {
      let labels = [];
      for (let i = this.props.layerOffset; i < node.data.length; i++) {
        labels.push(this.formatDate(this.context.layerStartDate, this.context.layerTimeIncrement, i));
      }
      let datasets = [
        {
          label: 'Nominal',
          data:
            node.type === "input"
              ? node.data.flatMap((layer, idx) => idx < this.props.layerOffset ? [] : [layer[2]])
              : node.data.flatMap((data, idx) => idx < this.props.layerOffset ? [] : [data]),
          fill: false,
          borderColor: "#50BFAF",
          lineTension: 0,
        },
        {
          label: 'Low',
          data:
            node.type === "input"
              ? node.data.flatMap((layer, idx) => idx < this.props.layerOffset ? [] : [layer[1]])
              : node.data.flatMap((data, idx) => idx < this.props.layerOffset ? [] : [data]),
          fill: false,
          borderColor: "#742774",
          lineTension: 0,
        },
        {
          label: 'High',
          data:
            node.type === "input"
              ? node.data.flatMap((layer, idx) => idx < this.props.layerOffset ? [] : [layer[3]])
              : node.data.flatMap((data, idx) => idx < this.props.layerOffset ? [] : [data]),
          fill: false,
          borderColor: "#BF2EBF",
          lineTension: 0,
        },
      ];
      let newChartData = { labels: labels, datasets: datasets };
      this.setState({ chartData: newChartData });
    }
  }

  componentWillReceiveProps(nextProps, nextContext) {
    if (nextProps.node !== "none") {
      this.setupChartData(nextProps.node);
    } else {
      this.setState({ chartData: { labels: [], datasets: [] } });
    }
  }

  render() {
    return (
      <div className="line-chart-container">
        <Line
          data={this.state.chartData}
          height={100}
          options={{
            layout: { padding: { left: 0, right: 0, top: 0, bottom: 50 } },
          }}
        />
      </div>
    );
  }
}
NodeDataChart.contextType = NodesContext;

export default NodeDataChart;
