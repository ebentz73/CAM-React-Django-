import React, {Component} from "react";
import {FormControl, MenuItem, Select, InputLabel} from "@material-ui/core";

class InputCategoryPage extends Component {
    constructor(props) {
        super(props);
        this.state = {
            nodes: {},
            filters: props.filters
        }

        this.toggleTable = this.toggleTable.bind(this);
        this.fetchNodesBySolution = this.fetchNodesBySolution.bind(this);
        this.changeFilterOption = this.changeFilterOption.bind(this);
    }

    fetchNodesBySolution(solution_id){
        fetch('http://' + window.location.host + '/api/node/solution=' + solution_id)
            .then(response => {
                return response.json();
            })
            .then(response => {
                let nodes = {};
                response.map(node => {
                    if (node.tags.length > 0)
                        nodes[node.id] = {name: node.name, tags: node.tags, tableToggle: false, visible: true};
                });
                this.setState({nodes: nodes});
            })
            .catch(err => {
                console.log(err);
            });
        fetch('http://' + window.location.host + '/api/node-data/solution=' + solution_id)
            .then(response => {
                return response.json();
            })
            .then(response => {
                let nodes = {...this.state.nodes};
                response.input_nodes.map(node => {
                    if (nodes[node.node] !== undefined) {
                        nodes[node.node].data = node.default_data;
                        nodes[node.node].type = 'input';
                    }
                });
                response.const_nodes.map(node => {
                    if (nodes[node.node] !== undefined) {
                        nodes[node.node].data = node.default_data;
                        nodes[node.node].type = 'const';
                    }
                });
                this.setState({nodes: nodes});
            })
            .catch(err => {
                console.log(err);
            });
    }

    componentDidMount() {
        this.fetchNodesBySolution('31');
    }

    toggleTable(node_id) {
        let newNodes = {...this.state.nodes};
        newNodes[node_id].tableToggle = !newNodes[node_id].tableToggle;
        this.setState({nodes: newNodes});
    }

    changeFilterOption(event, cat_id) {
        let newFilters = {...this.state.filters};
        newFilters[cat_id].selected = event.target.value;

        // Filter nodes
        let newNodes = {...this.state.nodes};
        console.log(newFilters);
        Object.keys(newNodes).map(node_id => {
            let node = newNodes[node_id];
            let newVisible = false;
            for (let i = 0; i < node.tags.length; i++){
                if (newFilters[cat_id].options[Object.keys(newFilters[cat_id].options)[newFilters[cat_id].selected]].tag.includes(node.tags[i])){
                    newVisible = true;
                }
            }
            node.visible = newVisible;
        });
        this.setState({filters: newFilters, nodes: newNodes});
    }

    render() {
        return (
            <div>
                {/* Filters */}
                <div className="filters">
                    {Object.keys(this.state.filters).map((cat_id, index) => {
                        let category = this.state.filters[cat_id];
                        return (
                            <div key={index}>
                                <FormControl>
                                    <InputLabel id={"filters-label-" + index}>{category.name}</InputLabel>
                                    <Select labelId={"filters-label-" + index} value={category.selected}
                                            onChange={(e) => this.changeFilterOption(e, cat_id)}>
                                        {Object.keys(category.options).map((option_id, index) => {
                                            let option = category.options[option_id];
                                            return(
                                                <MenuItem key={index} value={index}>{option.display_name}</MenuItem>
                                            );
                                        })}
                                        <MenuItem key={index} value={-1}>All</MenuItem>
                                    </Select>
                                </FormControl>

                            </div>
                        );
                    })}
                </div>

                {/* Nodes */}
                <div className="nodes">
                    {Object.keys(this.state.nodes).map((node_id, index) => {
                        let node = this.state.nodes[node_id];
                        if (!node.visible) return;
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

export default InputCategoryPage;