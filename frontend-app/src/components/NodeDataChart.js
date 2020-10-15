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
    }

    setupChartData(node){
        if (node !== undefined && node.data !== undefined) {
            let labels = [];
            for (let i = 0; i < node.data.length; i++) {
                labels.push(i);
            }
            let datasets = [{
                label: node.name,
                data: node.data.map(layer => layer[2]),
                fill: false,
                borderColor: "#742774",
                lineTension: 0
            }];
            this.setState({chartData: {labels: labels, datasets: datasets}});
        }
    }

    componentWillReceiveProps(nextProps, nextContext) {
        this.setupChartData(nextProps.node);
    }

    componentDidMount() {
        this.setupChartData(this.props.node);
    }

    render() {
        return (
            <div className="line-chart-container">
                <Line data={this.state.chartData}/>
            </div>
        );
    }
}

export default NodeDataChart;