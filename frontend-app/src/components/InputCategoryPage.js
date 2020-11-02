import React, {Component} from "react";
import {ComboBox, Stack, PrimaryButton, Text, ScrollablePane, DefaultButton} from '@fluentui/react';
import Node from "./Node";
import ConstantNodes from "./ConstantNodes";
import {Line} from "react-chartjs-2";
import NodeDataChart from './NodeDataChart';
import {ChevronDownIcon, ChevronUpIcon} from "@fluentui/react-icons";
import InputNodeTable from "./InputNodeTable";
import ConstNodeTable from "./ConstNodeTable";
import NodeTable from "./NodeTable";

class InputCategoryPage extends Component {
    constructor(props) {
        super(props);
        this.state = {
            nodes: props.nodes,
            filters: props.filters,
            categoryNodes: [],
            chartData: {},
            nodeOnChart: 'none',
            toggleFiltersBox: false,
            currentNodeID: '',
            currentNodeData: {},
            currentNodeType: ''
        }

        this.changeFilterOption = this.changeFilterOption.bind(this);
        this.filterNodesByInputCategory = this.filterNodesByInputCategory.bind(this);
        this.changeNodeShownOnChart = this.changeNodeShownOnChart.bind(this);
        this.toggleFiltersBox = this.toggleFiltersBox.bind(this);
        this.setCurrentNode = this.setCurrentNode.bind(this);
    }

    setCurrentNode(nodeId) {
        this.setState({
            currentNodeID: nodeId,
            currentNodeData: this.state.nodes[nodeId].data,
            currentNodeType: this.state.nodes[nodeId].type,
            nodeOnChart: this.state.nodes[nodeId]
        });
    }

    changeNodeShownOnChart(e, node_id) {
        e.stopPropagation();
        this.setState({nodeOnChart: this.state.nodes[node_id]});
    }

    filterNodesByInputCategory(categoryNodes) {
        this.setState({categoryNodes: categoryNodes.map(a => a.toString())});
    }

    componentWillReceiveProps(nextProps, nextContext) {
        if (nextProps.categoryNodes !== this.props.categoryNodes) {
            console.log('will-receieve'); //TODO: Remove
            // Change of Input Category Page
            this.filterNodesByInputCategory(nextProps.categoryNodes);
            this.setState({
            currentNodeID: '',
            currentNodeData: {},
            currentNodeType: '',
            nodeOnChart: 'none'
        });
        }

        if (nextProps.nodes !== this.props.nodes) {
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

    toggleFiltersBox() {
        this.setState({toggleFiltersBox: !this.state.toggleFiltersBox});
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
            <React.Fragment>
                <div className="ms-Grid-row">
                    <div className='tab-title'><Text variant='xLarge'>{this.props.name}</Text></div>
                    {/* Filters */}
                    <div className="filters-label-box">
                        <div className="filters-box-header" onClick={this.toggleFiltersBox}>
                            <Text className="filters-label">Filters</Text>
                            {this.state.toggleFiltersBox ?
                                <ChevronUpIcon className="filters-label-chevron"/> :
                                <ChevronDownIcon className="filters-label-chevron"/>
                            }
                        </div>

                        {this.state.toggleFiltersBox &&
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
                                    <div key={index} className="filter-dropdown">
                                        <ComboBox options={options} autoComplete="on" label={category.name}
                                                  selectedKey={category.selected.toString()}
                                                  onChange={(e, val) =>
                                                      this.changeFilterOption(e, val, cat_id)}/>
                                    </div>
                                );
                            })}
                        </div>
                        }
                    </div>
                </div>

                {/* Chart */
                }
                <div className="ms-Grid-row">
                    <div className="ms-Grid-col ms-md12">
                        <NodeDataChart node={this.state.nodeOnChart}/>
                    </div>
                </div>

                {/* Nodes */
                }
                <div className="ms-Grid-row">
                    <div className="ms-Grid-col ms-md4 node-scroll-pane">
                        <div className="">
                            <div className="nodes">
                                {/* Input Nodes */}
                                {this.state.categoryNodes.map((node_id, index) => {
                                    let node = this.state.nodes[node_id];

                                    // Filter by role
                                    let inRole = false;
                                    if (!inRole) {
                                        node.tags.forEach(tag => {
                                            this.props.roles.forEach(role => {
                                                inRole |= tag.includes('ROLE==' + role)
                                            });
                                        });
                                    }
                                    if (!node.visible | !inRole) return;
                                    return (
                                        <Node key={node_id} nodeId={node_id} node={node} onClick={() => this.setCurrentNode(node_id)}
                                              changeChartData={this.changeNodeShownOnChart}/>
                                    );
                                })}
                            </div>
                        </div>
                    </div>
                    <div className="ms-Grid-col ms-md8 node-scroll-pane">
                        <NodeTable type={this.state.currentNodeType} nodeId={this.state.currentNodeID}
                                   data={this.state.currentNodeData} />

                    </div>
                </div>
                {/*Navigation Buttons*/}
                <div className="ms-Grid-row">
                    <div className="ms-Grid-col ms-md12">
                        <div className="navigation-buttons">
                            <Stack horizontal horizontalAlign="space-between">
                                <Stack.Item align="start">
                                    <PrimaryButton text="Previous"
                                                   onClick={() => this.props.changeTab(this.props.index - 1)}/>
                                </Stack.Item>
                                <Stack.Item align="end">
                                    <DefaultButton text="Save & exit" onClick={this.props.postScenario} />
                                </Stack.Item>
                                <Stack.Item align="end">
                                    <PrimaryButton text="Next"
                                                   onClick={() => this.props.changeTab(this.props.index + 1)}/>
                                </Stack.Item>
                            </Stack>
                        </div>
                    </div>
                </div>
            </React.Fragment>
        )
    }
}

export default InputCategoryPage;