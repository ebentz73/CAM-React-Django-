import React, {Component} from "react";
import {render} from "react-dom";

class Phase extends Component {
    constructor(props) {
        super(props);
        this.state = {
            nodes: [],
            nodes_test: [
                {name: 'IP Forecast', data: [['One', 'Two'], ['Three', 'Four'], ['Five', 'Six', 'Seven']]},
                {name: 'Pilot Demand', data: [['One', 'Two'], ['Three']]},
                {name: 'Reservist', data: [['One', 'Two'], ['Three']]}
            ],
            filters: ['MDS: F16', 'Base: Laughlin',
                'BUNO: (All)', 'Clear all filters']
        }

        this.toggleTable = this.toggleTable.bind(this);
        this.fetchNodesByModel = this.fetchNodesByModel.bind(this);
    }

    fetchNodesByModel(model_id){
        fetch('http://' + window.location.host + '/api/node/' + model_id)
            .then(response => {
                return response.json();
            })
            .then(response => {
                let nodes = {};
                response.map(node => {
                    nodes[node.id] = {name: node.name, tags: node.tags, tableToggle: false};
                });
                this.setState({nodes: nodes});
            })
            .catch(err => {
                console.log(err);
            });
        fetch('http://' + window.location.host + '/api/node-data/' + model_id)
            .then(response => {
                return response.json();
            })
            .then(response => {
                let nodes = {...this.state.nodes};
                response.input_nodes.map(node => {
                    nodes[node.node].data = node.default_data;
                    nodes[node.node].type = 'input';
                });
                response.const_nodes.map(node => {
                    nodes[node.node].data = node.default_data;
                    nodes[node.node].type = 'const';
                });
                this.setState({nodes: nodes});
            })
            .catch(err => {
                console.log(err);
            });
    }

    componentDidMount() {
        this.fetchNodesByModel('18');
    }

    toggleTable(node_id) {
        let newNodes = {...this.state.nodes};
        newNodes[node_id].tableToggle = !newNodes[node_id].tableToggle;
        this.setState({nodes: newNodes});
    }

    render() {
        return (
            <div>
                {/* Filters */}
                <div className="filters">
                    {this.state.filters.map((filter, index) => {
                        return (
                            <div key={index}>{filter}</div>
                        )
                    })}
                </div>

                {/* Nodes */}
                <div className="nodes">
                    {Object.keys(this.state.nodes).map((node_id, index) => {
                        let node = this.state.nodes[node_id];
                        return (
                            <div key={index}>
                                <div className="node-header" onClick={() => this.toggleTable(node_id)}>
                                    <div className="label">{node.name}</div>
                                    <div className="changes-toggle">Changes</div>
                                </div>
                                {node.tableToggle &&
                                <div className="node-table">
                                    <table>
                                        <tbody>
                                        {node.type === 'input' && node.data[0].map((_, colIndex) => {
                                            return (
                                                <tr key={colIndex}>
                                                    {node.data.map((row, index) => {
                                                        return(<td key={index}>{row[colIndex]}</td>);
                                                    })}
                                                </tr>
                                            );
                                        })}
                                        {node.type === 'const' &&
                                            <tr>
                                                {node.data.map((val, index) => {
                                                    return (<td key={{index}}>{val}</td>);
                                                })}
                                            </tr>
                                        }
                                        </tbody>
                                    </table>
                                </div>
                                }
                            </div>
                        );
                    })}
                </div>
            </div>
        )
    }
}

export default Phase;