import React, {Component} from "react";
import {ComboBox, Stack, PrimaryButton, Text} from '@fluentui/react';
import Node from "./Node";
import OtherNodes from "./OtherNodes";
import {Line} from "react-chartjs-2";
import NodeDataChart from './NodeDataChart';

class InputCategoryPage extends Component {
    constructor(props) {
        super(props);
        this.state = {
            nodes: props.nodes,
            filters: props.filters,
            categoryNodes: [],
            chartData: {},
            nodeOnChart: 'none'
        }

        this.changeFilterOption = this.changeFilterOption.bind(this);
        this.filterNodesByInputCategory = this.filterNodesByInputCategory.bind(this);
        this.changeNodeShownOnChart = this.changeNodeShownOnChart.bind(this);
    }

    changeNodeShownOnChart(e, node_id){
        e.stopPropagation();
        this.setState({nodeOnChart: this.state.nodes[node_id]});
    }

    filterNodesByInputCategory(categoryNodes) {
        this.setState({categoryNodes: categoryNodes.map(a => a.toString())});
    }

    componentWillReceiveProps(nextProps, nextContext) {
        if (nextProps.categoryNodes !== this.props.categoryNodes) {
            this.filterNodesByInputCategory(nextProps.categoryNodes);
        }

        if(nextProps.nodes !== this.props.nodes) {
            this.setState({nodes: nextProps.nodes});
        }
    }

    componentDidMount() {
        this.filterNodesByInputCategory(this.props.categoryNodes);
    }

    isNodeVisible(node) {
        let visible = true;
        Object.keys(node.selectedCategories).map(cat_id => {
            visible &= node.selectedCategories[cat_id];
        })
        return visible;
    }

    changeFilterOption(event, value, cat_id) {
        let newFilters = {...this.state.filters};
        let selectedKey = parseInt(value.key);
        newFilters[cat_id].selected = selectedKey;

        // Filter nodes
        let newNodes = {...this.state.nodes};
        Object.keys(newNodes).map(node_id => {
            let node = newNodes[node_id];
            if (selectedKey === -1) {
                node.selectedCategories[cat_id] = true;
            } else {
                let selectedOptionMatchTag = false;
                for (let i = 0; i < node.tags.length; i++) {
                    let a = newFilters[cat_id].selected;
                    let b = newFilters[cat_id].options;
                    if (newFilters[cat_id].options[a].tag.includes(node.tags[i])) {
                        selectedOptionMatchTag = true;
                    }
                }
                node.selectedCategories[cat_id] = selectedOptionMatchTag;
            }

            node.visible = this.isNodeVisible(node);
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
                        let options = [];
                        Object.keys(category.options).map((opt_id, index) => {
                            let option = category.options[opt_id];
                            options.push({key: opt_id, text: option.display_name});
                        });
                        options.push({key: '-1', text: 'All'});
                        return (
                            <div key={index}>
                                <ComboBox options={options} autoComplete="on" label={category.name}
                                          selectedKey={category.selected.toString()}
                                          onChange={(e, val) =>
                                              this.changeFilterOption(e, val, cat_id)}/>

                            </div>
                        );
                    })}
                </div>

                {/* Chart */}
                <NodeDataChart node={this.state.nodeOnChart} />

                {/* Nodes */}
                <div className="nodes">
                    {/* Input Nodes */}
                    {this.state.categoryNodes.map((node_id, index) => {
                        let node = this.state.nodes[node_id];
                        if (!node.visible || node.type === 'const') return;
                        return (
                            <Node key={node_id} nodeId={node_id} node={node} changeChartData={this.changeNodeShownOnChart} />
                        );
                    })}

                    {/* Other Nodes */}
                    <OtherNodes nodes={this.state.nodes}/>
                </div>
                {/*Navigation Buttons*/}
                <div className="navigation-buttons">
                    <Stack horizontal horizontalAlign="space-between">
                        <Stack.Item align="start">
                            <PrimaryButton text="Previous" onClick={() => this.props.changeTab(this.props.index - 1)}/>
                        </Stack.Item>
                        <Stack.Item align="end">
                            <PrimaryButton text="Next" onClick={() => this.props.changeTab(this.props.index + 1)}/>
                        </Stack.Item>
                    </Stack>
                </div>
            </div>
        )
    }
}

export default InputCategoryPage;