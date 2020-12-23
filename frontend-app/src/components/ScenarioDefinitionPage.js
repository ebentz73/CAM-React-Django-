import React, { Component } from "react";
import {
  Pivot,
  PivotItem,
  Dropdown,
  Breadcrumb,
  Dialog,
  DialogType,
  DialogFooter,
  PrimaryButton,
  DefaultButton,
} from "@fluentui/react";
import { withRouter } from "react-router";
import SetupPage from "./SetupPage";
import InputCategoryPage from "./InputCategoryPage";
import NodesContext from "./NodesContext";
import ReviewPage from "./ReviewPage";
import NavBar from "./NavBar";
import ScenarioProgressStep from "./ScenarioProgressStep";
import PowerBIReport from "./PowerBIReport";

function getCookie(name) {
  return (
    (name = (document.cookie + ";").match(new RegExp(name + "=.*;"))) &&
    name[0].split(/=|;/)[1]
  );
}

const csrf_token = getCookie("csrftoken");

const dialogStyles = { main: { maxWidth: 450 } };

const dialogContentProps = {
  type: DialogType.normal,
  title: "Review Changes",
  closeButtonArialLabel: "Close",
  subText: "You have made changes. Do you want to discard or save them?",
};

class ScenarioDefinitionPage extends Component {
  constructor(props) {
    super(props);
    this.state = {
      filters: {},
      nodes: {},
      tab: "setup",
      inputCategories: {},
      inputCategoryOrder: [],
      category: "",
      category_idx: -1,
      scenario_name: "New Scenario",
      solution_name: "",
      model_date: "",
      status: null,
      description: "",
      input_values: {},
      nodes_changed: 0,
      roles: {},
      activeRoles: [],
      isLoading: true,
      layer_offset: 0,
      layer_time_increment: "month",
      hideDialog: true,
      lastLocation: null,
      confirmedNavigation: false,
    };

    this.onClickCategory = this.onClickCategory.bind(this);
    this.onClickSetup = this.onClickSetup.bind(this);
    this.filtersBySolution = this.filtersBySolution.bind(this);
    this.fetchNodesBySolution = this.fetchNodesBySolution.bind(this);
    this.fetchNodeDataByScenario = this.fetchNodeDataByScenario.bind(this);
    this.fetchScenarioMetadata = this.fetchScenarioMetadata.bind(this);
    this.fetchSolutionMetadata = this.fetchSolutionMetadata.bind(this);

    this.createOrUpdateScenario = this.createOrUpdateScenario.bind(this);
    this.createOrUpdateScenNodeDatas = this.createOrUpdateScenNodeDatas.bind(
      this
    );
    this.changeTab = this.changeTab.bind(this);

    this.updateConstNodeData = this.updateConstNodeData.bind(this);
    this.updateInputNodeData = this.updateInputNodeData.bind(this);
    this.updateInputRowData = this.updateInputRowData.bind(this);
    this.copyToAllLayers = this.copyToAllLayers.bind(this);

    this.changeScenarioName = this.changeScenarioName.bind(this);
    this.changeScenarioDesc = this.changeScenarioDesc.bind(this);
    this.changeModelDate = this.changeModelDate.bind(this);
    this.changeRole = this.changeRole.bind(this);
    this.changeInputs = this.changeInputs.bind(this);
    this.changeInputDataSet = this.changeInputDataSet.bind(this);
    this.discard = this.discard.bind(this);

    this.toggleHideDialog = this.toggleHideDialog.bind(this);
    this.goScenarioListPage = this.goScenarioListPage.bind(this);
    this.goHomepage = this.goHomepage.bind(this);

    this.setupProps = {
      updateName: this.changeScenarioName,
      updateDesc: this.changeScenarioDesc,
      updateDate: this.changeModelDate,
    };

    this.solution_id = this.props.match.params["id"];
    this.scenario_id = this.props.match.params["scenarioId"];
  }

  componentDidMount() {
    if (this.scenario_id !== undefined) {
      this.fetchScenarioMetadata();
    }
    this.fetchSolutionMetadata();
    this.filtersBySolution(this.solution_id);
    this.fetchNodesBySolution(this.solution_id);
  }

  goHomepage() {
    let nextLocation = `${window.location.protocol}//${window.location.host}/frontend-app/home`;
    if (this.state.nodes_changed > 0) {
      this.toggleHideDialog(nextLocation);
    } else {
      window.location.href = nextLocation;
    }
  }

  goScenarioListPage() {
    let nextLocation = `${window.location.protocol}//${window.location.host}/frontend-app/solution/${this.solution_id}/scenario`;
    if (this.state.nodes_changed > 0) {
      this.toggleHideDialog(nextLocation);
    } else {
      window.location.href = nextLocation;
    }
  }

  discard() {
    this.setState({ nodes_changed: 0 });
    window.location.href = this.state.lastLocation;
  }

  toggleHideDialog(location) {
    this.setState((prevState) => ({
      hideDialog: !prevState.hideDialog,
      lastLocation: location,
    }));
  }

  changeScenarioName(val) {
    this.setState({ scenario_name: val });
  }

  changeScenarioDesc(val) {
    this.setState({ description: val });
  }

  changeModelDate(val) {
    this.setState({ model_date: val });
  }

  changeInputs(input_id, node_id, val) {
    let inputValues = { ...this.state.input_values };
    if (!inputValues.hasOwnProperty(input_id)) {
      inputValues[input_id] = {};
    }
    inputValues[input_id].value = val;
    inputValues[input_id].isIds = false;

    let nodes = { ...this.state.nodes };
    let node = nodes[node_id];
    let dirty = this.state.nodes_changed;

    for (let layer = 0; layer < node.data.length; layer++) {
      const isArray = Array.isArray(node.data[layer]);
      if (isArray) {
        // Assume input node
        node.data[layer].forEach((part, index) => {
          node.data[index] = val;
        });
      } else {
        // Otherwise assume constant node
        node.data[layer] = val;
      }
    }

    if (!node.dirty) {
      dirty++;
    }
    node.dirty = true;

    this.setState({
      nodes: nodes,
      nodes_changed: dirty,
      input_values: inputValues,
    });
  }

  changeInputDataSet(input_id, val) {
    let inputValues = { ...this.state.input_values };
    if (!inputValues.hasOwnProperty(input_id)) {
      inputValues[input_id] = {};
    }
    inputValues[input_id].value = val;
    inputValues[input_id].isIds = true;

    this.setState({ input_values: inputValues });
  }

  changeRole(e, role) {
    let newRoles = [...this.state.activeRoles];
    if (role.selected) {
      newRoles.push(role.key);
    } else {
      let index = newRoles.indexOf(role.key);
      if (index !== -1) {
        newRoles.splice(index, 1);
      }
    }
    this.setState({ activeRoles: newRoles });
  }

  changeTab(val) {
    if (val <= -1) {
      this.setState({ tab: "setup", category_idx: -1 });
    } else if (val >= Object.keys(this.state.inputCategories).length) {
      this.setState({
        tab: "review",
        category_idx: Object.keys(this.state.inputCategories).length,
      });
    } else {
      this.setState({
        tab: "category",
        category_idx: val,
        category: this.state.inputCategoryOrder[val],
      });
    }
  }

  createOrUpdateScenario() {
    const { history } = this.props;
    let formatDate = (date) => {
      let year = date.getFullYear();
      let month = `${date.getMonth() + 1}`.padStart(2, "0");
      let day = `${date.getDate()}`.padStart(2, "0");
      return `${year}-${month}-${day}`;
    };

    const input_data_sets = Object.values(this.state.input_values)
      .map((input) => {
        if (input.isIds) return input.value;
      })
      .filter((value) => value !== undefined);

    let url = `${window.location.protocol}//${window.location.host}/api/v1/solutions/${this.solution_id}/scenarios/`;
    let method = "POST";
    let body = {
      name: this.state.scenario_name,
      is_adhoc: true,
      layer_date_start: formatDate(this.state.model_date),
      input_data_sets: input_data_sets,
      run_eval: true,
    };
    if (this.scenario_id) {
      url += `${this.scenario_id}/`;
      method = "PATCH";
      body.id = parseInt(this.scenario_id);
    }
    return fetch(url, {
      method: method,
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
        "X-CSRFToken": csrf_token,
      },
      body: JSON.stringify(body),
    })
      .then((resp) => {
        return resp.json();
      })
      .then((resp) => {
        this.createOrUpdateScenNodeDatas();
        history.push(`/frontend-app/solution/${this.solution_id}/scenario`);
      })
      .catch((err) => {
        console.error(err);
      });
  }

  createOrUpdateScenNodeDatas() {
    // Only post data for nodes with changed values
    Object.keys(this.state.nodes)
      .filter((node_id) => this.state.nodes[node_id].dirty)
      .map((node_id) => {
        let node = this.state.nodes[node_id];
        let method = "POST";
        let body = {
          node: node_id,
          default_data: this.state.nodes[node_id].data,
          scenario: parseInt(this.scenario_id),
          is_model: false,
          resourcetype:
            node.type === "input" ? "InputNodeData" : "ConstNodeData",
        };
        let url = `${window.location.protocol}//${window.location.host}/api/v1/solutions/${this.solution_id}/scenarios/${this.scenario_id}/nodedatas/`;
        if (node.hasOwnProperty("id")) {
          method = "PUT";
          body.id = node.id;
          url += node.id + "/";
        }
        fetch(url, {
          method: method,
          headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
            "X-CSRFToken": csrf_token,
          },
          body: JSON.stringify(body),
        }).catch((err) => {
          console.error(err);
        });
      });
  }

  updateInputNodeData(node_id, layer_idx, nom_idx, val) {
    let newNodes = { ...this.state.nodes };
    let newNumDirty = this.state.nodes_changed;
    newNodes[node_id].data[layer_idx][nom_idx] = val;
    if (!newNodes[node_id].dirty) newNumDirty++;
    newNodes[node_id].dirty = true;
    this.setState({ nodes: newNodes, nodes_changed: newNumDirty });
  }

  updateInputRowData(node_id, layer_idx, nom_idx, val) {
    for (let i = 0; i < this.state.nodes[node_id].data.length; i++) {
      let newNodes = { ...this.state.nodes };
      let newNumDirty = this.state.nodes_changed;
      newNodes[node_id].data[i][nom_idx] = val;
      if (!newNodes[node_id].dirty) newNumDirty++;
      newNodes[node_id].dirty = true;
      this.setState({ nodes: newNodes, nodes_changed: newNumDirty });
    }
  }

  updateConstNodeData(node_id, layer_idx, val) {
    let newNodes = { ...this.state.nodes };
    let newNumDirty = this.state.nodes_changed;
    newNodes[node_id].data[layer_idx] = val;
    if (!newNodes[node_id].dirty) newNumDirty++;
    newNodes[node_id].dirty = true;
    this.setState({ nodes: newNodes, nodes_changed: newNumDirty });
  }

  copyToAllLayers(node_id, layer_idx) {
    let newNodes = { ...this.state.nodes };
    let newNumDirty = this.state.nodes_changed;
    let numLayers = newNodes[node_id].data.length;
    for (let layer = 0; layer < numLayers; layer++) {
      for (let nom = 0; nom < 5; nom++) {
        newNodes[node_id].data[layer][nom] =
          newNodes[node_id].data[layer_idx][nom];
      }
    }
    if (!newNodes[node_id].dirty) newNumDirty++;
    newNodes[node_id].dirty = true;
    this.setState({ nodes: newNodes, nodes_changed: newNumDirty });
  }

  fetchNodeDataByScenario(scenario_id) {
    fetch(
      `${window.location.protocol}//${window.location.host}/api/v1/solutions/${this.solution_id}/scenarios/${scenario_id}/nodedatas/`
    )
      .then((response) => {
        return response.json();
      })
      .then((response) => {
        let nodes = { ...this.state.nodes };
        response.forEach((node) => {
          if (nodes[node.node] !== undefined) {
            nodes[node.node].data = node.default_data;
            nodes[node.node].id = node.id;
          }
        });
        this.setState({ nodes: nodes, isLoading: false });
      });
  }

  fetchNodesBySolution(solution_id) {
    // Fetching Nodes
    fetch(
      `${window.location.protocol}//${window.location.host}/api/v1/solutions/${solution_id}/nodes/`
    )
      .then((response) => {
        return response.json();
      })
      .then((response) => {
        let nodes = {};
        let newInputCategoryOrder = [];
        let newInputCategories = { ...this.state.inputCategories };
        let roles = {};
        response.forEach((node) => {
          // Only include nodes with tags
          if (node.tags.length > 0) {
            // Add initial node data to component state
            let node_obj = {
              name: node.name,
              tags: node.tags,
              visible: true,
              selectedCategories: {},
              dirty: false,
            };
            Object.keys(this.state.filters).forEach((cat_id) => {
              node_obj.selectedCategories[cat_id] = true;
            });
            nodes[node.id] = node_obj;

            // Retrieve input category from node if any
            node.tags.forEach((tag) => {
              if (tag.includes("CAM_INPUT_CATEGORY==")) {
                let input_category = tag.substring(
                  tag.lastIndexOf("=") + 1,
                  tag.length
                );
                if (newInputCategories.hasOwnProperty(input_category)) {
                  newInputCategories[input_category].push(node.id);
                } else {
                  newInputCategories[input_category] = [node.id];
                  newInputCategoryOrder.push(input_category);
                }
              }
              if (tag.includes("CAM_ROLE==")) {
                let role = tag.substring(tag.lastIndexOf("=") + 1, tag.length);
                roles[role] = role;
              }
            });
          }
        });
        newInputCategoryOrder.sort();
        this.setState({
          nodes: nodes,
          inputCategories: newInputCategories,
          inputCategoryOrder: newInputCategoryOrder,
          roles: roles,
        });
      })
      .catch((err) => {
        console.error(err);
      });

    // Fetching NodeDatas for corresponding Nodes
    fetch(
      `${window.location.protocol}//${window.location.host}/api/v1/solutions/${solution_id}/modelnodedatas/`
    )
      .then((response) => {
        return response.json();
      })
      .then((response) => {
        let nodes = { ...this.state.nodes };
        response.forEach((node) => {
          if (nodes[node.node] !== undefined) {
            nodes[node.node].data = node.default_data;
            if (node.resourcetype === "InputNodeData")
              nodes[node.node].type = "input";
            else nodes[node.node].type = "const";
          }
        });
        this.setState({ nodes: nodes });
        if (this.scenario_id >= 0) {
          this.fetchNodeDataByScenario(this.scenario_id);
        } else {
          this.setState({ isLoading: false });
        }
      })
      .catch((err) => {
        console.error(err);
      });
  }

  filtersBySolution(solution_id) {
    fetch(
      `${window.location.protocol}//${window.location.host}/api/v1/solutions/${solution_id}/filtercategories/`
    )
      .then((response) => {
        return response.json();
      })
      .then((response) => {
        let filters = {};
        response.forEach((category) => {
          filters[category.id] = {
            name: category.name,
            options: {},
            selected: -1,
          };
          category.filteroption_set.forEach((option) => {
            filters[category.id].options[option.id] = {
              display_name: option.display_name,
              tag: option.tag,
            };
          });
        });

        this.setState({ filters: filters });
      })
      .catch((err) => {
        console.error(err);
      });
  }

  fetchSolutionMetadata() {
    fetch(
      `${window.location.protocol}//${window.location.host}/api/v1/solutions/${this.solution_id}/`
    )
      .then((resp) => {
        return resp.json();
      })
      .then((resp) => {
        this.setState({
          layer_offset: resp.layer_offset,
          layer_time_increment: resp.layer_time_increment,
          solution_name: resp.name,
        });
      });
  }

  fetchScenarioMetadata() {
    fetch(
      `${window.location.protocol}//${window.location.host}/api/v1/solutions/${this.solution_id}/scenarios/${this.scenario_id}/`
    )
      .then((resp) => {
        return resp.json();
      })
      .then((resp) => {
        this.setState({
          scenario_name: resp.name,
          model_date: new Date(resp.layer_date_start),
          description: "",
          status: resp.status,
        });
      });
  }

  onClickSetup() {
    this.setState({ tab: "setup" });
  }

  onClickCategory(e, idx) {
    this.setState({
      tab: "category",
      category_idx: idx,
      category: this.state.inputCategoryOrder[idx],
    });
  }

  render() {
    const itemsWithHref = [
      {
        text: "Analytics Solutions",
        key: "f1",
        onClick: this.goHomepage,
      },
      {
        text: `${this.state.solution_name}`,
        key: "f2",
        onClick: this.goScenarioListPage,
      },
      { text: `${this.state.scenario_name}`, key: "f3", href: "#" },
    ];

    let nodesContext = {
      nodes: this.state.nodes,
      updateConstNodeData: this.updateConstNodeData,
      updateInputNodeData: this.updateInputNodeData,
      updateInputRowData: this.updateInputRowData,
      copyToAllLayers: this.copyToAllLayers,
      layerStartDate: this.state.model_date,
      layerTimeIncrement: this.state.layer_time_increment,
    };
    let pivotStyles = {
      root: {
        backgroundColor: "rgb(0, 99, 177)",
        marginLeft: "-20px",
        paddingLeft: "60px",
        marginRight: "-20px",
        paddingRight: "20px",
        boxShadow: "0px 1px 4px 1px rgb(194, 194, 194)",
        selectors: {
          ".ms-Pivot-link:hover": {
            backgroundColor: "rgb(4, 53,102)",
          },
          ".linkIsSelected-48::before": {
            backgroundColor: "white",
          },
        },
      },
      text: {
        color: "white",
      },
    };
    return (
      <React.Fragment>
        <NavBar />
        <Dialog
          hidden={this.state.hideDialog}
          onDismiss={this.toggleHideDialog}
          dialogContentProps={dialogContentProps}
        >
          <DialogFooter>
            <DefaultButton onClick={this.toggleHideDialog} text="Cancel" />
            <DefaultButton onClick={this.discard} text="Discard" />
            <PrimaryButton onClick={this.createOrUpdateScenario} text="Save" />
          </DialogFooter>
        </Dialog>
        <div className="ms-Grid grid-margin" dir="ltr">
          <Pivot styles={pivotStyles} className="pivot-margin">
            <PivotItem headerText="Input">
              <NodesContext.Provider value={nodesContext}>
                <div className="ms-Grid-row scenario-definition">
                  <div className="ms-Grid-col ms-md2 sidebar-left">
                    <div className="progress-sidebar">
                      <ScenarioProgressStep
                        index={-1}
                        includeStem={false}
                        changeTab={this.changeTab}
                        step={"Setup"}
                        activeStep={this.state.category_idx}
                      />
                      {this.state.inputCategoryOrder.map((cat_name, index) => {
                        return (
                          <ScenarioProgressStep
                            key={`step_${index}`}
                            index={index}
                            includeStem={true}
                            activeStep={this.state.category_idx}
                            changeTab={this.changeTab}
                            step={cat_name.substring(
                              cat_name.indexOf(".") + 1,
                              cat_name.length
                            )}
                          />
                        );
                      })}
                      <ScenarioProgressStep
                        index={Object.keys(this.state.inputCategories).length}
                        includeStem={true}
                        changeTab={this.changeTab}
                        step={"Review"}
                        activeStep={this.state.category_idx}
                      />
                    </div>
                  </div>
                  <div className="ms-Grid-col ms-md8 sidebar-right">
                    <Breadcrumb
                      items={itemsWithHref}
                      maxDisplayedItems={3}
                      ariaLabel="Breadcrumb with items rendered as links"
                      overflowAriaLabel="More links"
                    />
                    {/* Role Filter */}
                    <Dropdown
                      options={Object.keys(this.state.roles).map((role) => {
                        return { key: role, text: role };
                      })}
                      label="Roles"
                      multiSelect
                      styles={{ root: { margin: "0px 50px 20px 50px" } }}
                      selectedKeys={this.state.activeRoles}
                      onChange={(e, val) => this.changeRole(e, val)}
                    />
                    {/* Input Category Pages */}
                    {this.state.tab === "setup" && (
                      <SetupPage
                        solutionId={this.solution_id}
                        index={0}
                        changeTab={this.changeTab}
                        changeInputs={this.changeInputs}
                        changeInputDataSet={this.changeInputDataSet}
                        {...this.setupProps}
                        name={this.state.scenario_name}
                        desc={this.state.description}
                        date={this.state.model_date}
                        inputValues={this.state.input_values}
                        isReadOnly={this.state.status !== null}
                      />
                    )}
                    {this.state.tab === "category" && !this.state.isLoading && (
                      <InputCategoryPage
                        filters={this.state.filters}
                        nodes={this.state.nodes}
                        name={this.state.category.substring(
                          this.state.category.indexOf(".") + 1,
                          this.state.category.length
                        )}
                        index={this.state.category_idx}
                        roles={this.state.activeRoles}
                        changeTab={this.changeTab}
                        postScenario={this.createOrUpdateScenario}
                        categoryNodes={
                          this.state.inputCategories[this.state.category]
                        }
                        layerOffset={this.state.layer_offset}
                      />
                    )}
                    {this.state.tab === "review" && (
                      <ReviewPage
                        index={this.state.inputCategoryOrder.length}
                        postScenario={this.createOrUpdateScenario}
                        changeTab={this.changeTab}
                        name={this.state.scenario_name}
                        desc={this.state.description}
                        date={this.state.model_date}
                        nodesChanged={this.state.nodes_changed}
                        isReadOnly={this.state.status !== null}
                      />
                    )}
                  </div>
                </div>
              </NodesContext.Provider>
            </PivotItem>
            <PivotItem headerText="Results">
              <PowerBIReport
                history={this.props.history}
                solutionId={this.solution_id}
                scenarioId={this.scenario_id}
              />
            </PivotItem>
          </Pivot>
        </div>
      </React.Fragment>
    );
  }
}

export default withRouter(ScenarioDefinitionPage);
