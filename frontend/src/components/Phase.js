import React, {Component} from "react";
import {render} from "react-dom";

class Phase extends Component {
    constructor(props) {
        super(props);
        this.state = {
            toggleTable: [true, true, true],
            nodes_test: [],
            nodes: [
                {name: 'IP Forecast', data: [['One', 'Two'], ['Three', 'Four'], ['Five', 'Six', 'Seven']]},
                {name: 'Pilot Demand', data: [['One', 'Two'], ['Three']]},
                {name: 'Reservist', data: [['One', 'Two'], ['Three']]}
            ],
            filters: ['MDS: F16', 'Base: Laughlin',
                'BUNO: (All)', 'Clear all filters']
        }

        this.toggleTable = this.toggleTable.bind(this);
        this.fetchNodesByModel = this.fetchNodesByModel.bind(this);
        this.fetchDataByNode = this.fetchDataByNode.bind(this);
    }

    fetchDataByNode(node_id){
        fetch('http://' + window.location.host + '/api/input-node-data/' + node_id)
            .then(response => {
                return response.json();
            })
            .then(response => {
                console.log(response);//TODO: Remove
            })
            .catch(err => {
                console.log(err);
            });
        fetch('http://' + window.location.host + '/api/const-node-data/' + node_id)
            .then(response => {
                console.log(response); //TODO: Remove
                return response.json();
            })
            .then(response => {
                console.log(response);
            })
            .catch(err => {
                console.log(err);
            });
    }

    fetchNodesByModel(model_id){
        fetch('http://' + window.location.host + '/api/node/' + model_id)
            .then(response => {
                return response.json();
            })
            .then(response => {
                let nodes = [];
                response.map(node => {
                    nodes.push({id: node.id, name: node.name, tags: node.tags});
                });
                this.setState({nodes_test: nodes});
            })
            .catch(err => {
                console.log(err);
            });
    }

    componentDidMount() {
        this.fetchDataByNode('11717');
        this.fetchNodesByModel('8');
    }

    toggleTable(index) {
        let newToggleTable = this.state.toggleTable.slice();
        newToggleTable[index] = !newToggleTable[index];
        this.setState({toggleTable: newToggleTable});
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
                    {this.state.nodes.map((node, index) => {
                        return (
                            <div key={index}>
                                <div className="node-header" onClick={() => this.toggleTable(index)}>
                                    <div className="label">{node.name}</div>
                                    <div className="changes-toggle">Changes</div>
                                </div>
                                {this.state.toggleTable[index] &&
                                <div className="node-table">
                                    <table>
                                        <tbody>
                                        {this.state.nodes[index].data.map((row, index) => {
                                            return (
                                                <tr key={index}>
                                                    {row.map((data, index) => {
                                                        return(<td key={index}>{data}</td>);
                                                    })}
                                                </tr>
                                            );
                                        })}
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