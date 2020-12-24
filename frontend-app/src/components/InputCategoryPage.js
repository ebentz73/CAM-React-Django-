import React, { Component } from "react";
import {
  ComboBox,
  Stack,
  PrimaryButton,
  Text,
  DefaultButton,
} from "@fluentui/react";
import { SearchBox } from "office-ui-fabric-react/lib/SearchBox";
import { Spinner, SpinnerSize } from "office-ui-fabric-react/lib/Spinner";
import Node from "./Node";
import NodeDataChart from "./NodeDataChart";
import { ChevronDownIcon, ChevronUpIcon } from "@fluentui/react-icons";
import NodeTable from "./NodeTable";
import ConstantsListNode from "./ConstantsListNode";

class InputCategoryPage extends Component {
  constructor(props) {
    super(props);
    this.state = {
      nodes: props.nodes,
      filters: props.filters,
      categoryNodes: [],
      filteredCategoryNodes: [],
      chartData: {},
      nodeOnChart: "none",
      toggleFiltersBox: false,
      currentNodeID: "",
      currentNodeData: {},
      currentNodeType: "",
    };

    this.changeFilterOption = this.changeFilterOption.bind(this);
    this.setInputCategoryNodes = this.setInputCategoryNodes.bind(this);
    this.changeNodeShownOnChart = this.changeNodeShownOnChart.bind(this);
    this.toggleFiltersBox = this.toggleFiltersBox.bind(this);
    this.setCurrentNode = this.setCurrentNode.bind(this);
  }

  setCurrentNode(nodeId) {
    if (nodeId === "const") {
      this.setState({
        currentNodeID: "const",
        currentNodeData: {},
        currentNodeType: "const",
        nodeOnChart: "none",
      });
    } else {
      this.setState({
        currentNodeID: nodeId,
        currentNodeData: this.state.nodes[nodeId].data,
        currentNodeType: this.state.nodes[nodeId].type,
        nodeOnChart: this.state.nodes[nodeId],
      });
    }
  }

  changeNodeShownOnChart(e, node_id) {
    e.stopPropagation();
    this.setState({ nodeOnChart: this.state.nodes[node_id] });
  }

  setInputCategoryNodes(categoryNodes) {
    // Sort alphabetically

    categoryNodes.sort((a, b) => {
      if (this.props.nodes[a].name < this.props.nodes[b].name) return -1;
      if (this.props.nodes[a].name > this.props.nodes[b].name) return 1;
      return 0;
    });
    this.setState({ categoryNodes: categoryNodes.map((a) => a.toString()) });
    this.setState({
      filteredCategoryNodes: categoryNodes.map((a) => a.toString()),
    });
  }

  componentWillReceiveProps(nextProps, nextContext) {
    if (nextProps.categoryNodes !== this.props.categoryNodes) {
      // Change of Input Category Page
      this.setInputCategoryNodes(nextProps.categoryNodes);
      this.setState({
        currentNodeID: "",
        currentNodeData: {},
        currentNodeType: "",
        nodeOnChart: "none",
      });
    }

    if (nextProps.nodes !== this.props.nodes) {
      this.setState({ nodes: nextProps.nodes });
    }
  }

  componentDidMount() {
    this.setInputCategoryNodes(this.props.categoryNodes);
  }

  isNodeVisible(node) {
    let visible = true;
    Object.keys(node.selectedCategories).map((cat_id) => {
      visible &= node.selectedCategories[cat_id];
    });
    return visible;
  }

  toggleFiltersBox() {
    this.setState({ toggleFiltersBox: !this.state.toggleFiltersBox });
  }

  changeFilterOption(event, value, cat_id) {
    let newFilters = { ...this.state.filters };
    let selectedKey = parseInt(value.key);
    newFilters[cat_id].selected = selectedKey;

    // Filter nodes
    let newNodes = { ...this.state.nodes };
    Object.keys(newNodes).map((node_id) => {
      let node = newNodes[node_id];
      if (selectedKey === -1) {
        node.selectedCategories[cat_id] = true;
      } else {
        let selectedOptionMatchTag = false;
        for (let i = 0; i < node.tags.length; i++) {
          let selectedFilters = newFilters[cat_id].selected;
          if (
            newFilters[cat_id].options[selectedFilters].tag.includes(
              node.tags[i]
            )
          ) {
            selectedOptionMatchTag = true;
          }
        }
        node.selectedCategories[cat_id] = selectedOptionMatchTag;
      }

      node.visible = this.isNodeVisible(node);
    });
    this.setState({ filters: newFilters, nodes: newNodes });
  }

  render() {
    return (
      <React.Fragment>
        <div className="ms-Grid-row">
          {/* Filters */}
          <div className="filters-label-box">
            <div className="filters-box-header" onClick={this.toggleFiltersBox}>
              <Text className="filters-label">Filters</Text>
              {this.state.toggleFiltersBox ? (
                <ChevronUpIcon className="filters-label-chevron" />
              ) : (
                <ChevronDownIcon className="filters-label-chevron" />
              )}
            </div>

            {this.state.toggleFiltersBox && (
              <div className="filters">
                {Object.keys(this.state.filters).map((cat_id, index) => {
                  let category = this.state.filters[cat_id];
                  let options = [];
                  Object.keys(category.options).map((opt_id, index) => {
                    let option = category.options[opt_id];
                    options.push({ key: opt_id, text: option.display_name });
                  });
                  options.push({ key: "-1", text: "All" });
                  return (
                    <div key={index} className="filter-dropdown">
                      <ComboBox
                        options={options}
                        autoComplete="on"
                        label={category.name}
                        selectedKey={category.selected.toString()}
                        onChange={(e, val) =>
                          this.changeFilterOption(e, val, cat_id)
                        }
                      />
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Chart */}
        <div className="ms-Grid-row">
          <div className="ms-Grid-col ms-md12">
            {/* {this.state.nodeOnChart !== "none" ? ( */}
            <NodeDataChart
              node={this.state.nodeOnChart}
              layerOffset={this.props.layerOffset}
            />
            {/* ) : (
            <Spinner size={SpinnerSize.large} />
            )} */}
          </div>
        </div>

        {/* Nodes */}
        <div className="ms-Grid-row">
          <div className="ms-Grid-col ms-md4 node-scroll-pane">
            <div className="">
              <div className="nodes">
                {/* Input Nodes */}
                <SearchBox
                  placeholder="Search nodes"
                  onChange={(e, searchStr) => {
                    let searchResult = [];
                    this.state.categoryNodes.map((node_id, index) => {
                      let node = this.state.nodes[node_id];
                      if (
                        node.name
                          .toLowerCase()
                          .includes(searchStr.toLowerCase())
                      ) {
                        searchResult.push(node_id);
                      }
                    });
                    this.setState({
                      filteredCategoryNodes: searchResult,
                      currentNodeID: "",
                      currentNodeData: {},
                      currentNodeType: "",
                      nodeOnChart: "none",
                    });
                  }}
                />
                {this.state.filteredCategoryNodes.map((node_id, index) => {
                  let node = this.state.nodes[node_id];

                  // Filter by role
                  let inRole = false;
                  node.tags.forEach((tag) => {
                    this.props.roles.forEach((role) => {
                      inRole |= tag.includes("CAM_ROLE==" + role);
                    });
                  });
                  if (!node.visible | !inRole | (node.type === "const")) return;
                  return (
                    <Node
                      className="highlight"
                      key={node_id}
                      nodeId={node_id}
                      node={node}
                      isSelected={this.state.currentNodeID === node_id}
                      onClick={() => this.setCurrentNode(node_id)}
                      changeChartData={this.changeNodeShownOnChart}
                    />
                  );
                })}
                <ConstantsListNode
                  constantNodes={this.state.filteredCategoryNodes.filter(
                    (node_id) => this.state.nodes[node_id].type === "const"
                  )}
                  onClick={() => this.setCurrentNode("const")}
                  isSelected={this.state.currentNodeID === "const"}
                />
              </div>
            </div>
          </div>
          <div className="ms-Grid-col ms-md8 node-scroll-pane">
            {/* {this.state.currentNodeData.length > 0 ? ( */}
            <NodeTable
              type={this.state.currentNodeType}
              nodeId={this.state.currentNodeID}
              data={this.state.currentNodeData}
              constantNodes={this.state.filteredCategoryNodes.filter(
                (node_id) => this.state.nodes[node_id].type === "const"
              )}
              layerOffset={this.props.layerOffset}
              nodeOnChart={this.state.nodeOnChart}
            />
            {/* ) : (
              <Spinner size={SpinnerSize.large} />
            )} */}
          </div>
        </div>
        {/*Navigation Buttons*/}
        <div className="ms-Grid-row">
          <div className="ms-Grid-col ms-md12">
            <div className="navigation-buttons">
              <Stack horizontal horizontalAlign="space-between">
                <Stack.Item align="start">
                  <PrimaryButton
                    text="Previous"
                    onClick={() => this.props.changeTab(this.props.index - 1)}
                  />
                </Stack.Item>
                <Stack.Item align="end">
                  <DefaultButton
                    text="Save & exit"
                    onClick={this.props.postScenario}
                  />
                </Stack.Item>
                <Stack.Item align="end">
                  <PrimaryButton
                    text="Next"
                    onClick={() => this.props.changeTab(this.props.index + 1)}
                  />
                </Stack.Item>
              </Stack>
            </div>
          </div>
        </div>
      </React.Fragment>
    );
  }
}

export default InputCategoryPage;
