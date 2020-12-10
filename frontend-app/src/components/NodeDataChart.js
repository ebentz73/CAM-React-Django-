import React, {Component} from "react";
import {Line} from "react-chartjs-2";

class NodeDataChart extends Component {
    constructor(props) {
        super(props);

        this.state = {
            chartData: {
                labels: [],
                datasets: []
            }
        }

        this.months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    }

    setupChartData(node){
        if (node !== undefined && node.data !== undefined) {
            let labels = [];
            for (let i = this.props.layerOffset; i < node.data.length; i++) {
                labels.push(this.months[i % 12]);
            }
            let chartData = [];
            if (node.type === 'input') {
                chartData = node.data.flatMap((layer, idx) => idx < this.props.layerOffset ? [] : [layer[2]]);
            } else {
                chartData = node.data.flatMap((data, idx) => idx < this.props.layerOffset ? [] : [data]);
            }
            let datasets = [{
                label: node.name,
                data: chartData,
                fill: false,
                borderColor: "#742774",
                lineTension: 0
            }];
            let newChartData = {labels: labels, datasets: datasets};
            this.setState({chartData: newChartData});
        }
    }

    componentWillReceiveProps(nextProps, nextContext) {
        if (nextProps.node !== 'none') {
            this.setupChartData(nextProps.node);
        } else {
            this.setState({chartData: {labels: [], datasets: []}});
        }
    }

    render() {
        return (
            <div className="line-chart-container">
                <Line data={this.state.chartData} options={{layout: {padding: {left: 0, right: 0, top: 0, bottom: 50}}}}/>
            </div>
        );
    }
}

export default NodeDataChart;