import React, {Component} from "react";
import {PrimaryButton, Text} from "@fluentui/react";
import SetupPage from "./SetupPage";
import InputCategoryPage from "./InputCategoryPage";
import NodesContext from "./NodesContext";
import ReviewPage from "./ReviewPage";
import NavBar from "./NavBar";
import ScenarioProgressStep from "./ScenarioProgressStep";

function getCookie(name) {
  return (name = (document.cookie + ';').match(new RegExp(name + '=.*;'))) && name[0].split(/=|;/)[1];
}

const csrf_token = getCookie('csrftoken');

class ScenarioDefinitionPage extends Component {
    constructor(props) {
        super(props);
        this.state = {
            filters: {},
            nodes: {},
            tab: 'setup',
            inputCategories: {},
            inputCategoryOrder: [],
            category: '',
            category_idx: -1,
            scenario_name: '',
            model_date: '',
            description: '',
            nodes_changed: 0
        };

        this.onClickCategory = this.onClickCategory.bind(this);
        this.onClickSetup = this.onClickSetup.bind(this);
        this.filtersBySolution = this.filtersBySolution.bind(this);
        this.fetchNodesBySolution = this.fetchNodesBySolution.bind(this);
        this.postScenario = this.postScenario.bind(this);
        this.postScenNodeDatas = this.postScenNodeDatas.bind(this);
        this.changeTab = this.changeTab.bind(this);


        this.updateConstNodeData = this.updateConstNodeData.bind(this);
        this.updateInputNodeData = this.updateInputNodeData.bind(this);
        this.copyToAllLayers = this.copyToAllLayers.bind(this);

        this.changeScenarioName = this.changeScenarioName.bind(this);
        this.changeScenarioDesc = this.changeScenarioDesc.bind(this);
        this.changeModelDate = this.changeModelDate.bind(this);

        this.setupProps = {
            updateName: this.changeScenarioName,
            updateDesc: this.changeScenarioDesc,
            updateDate: this.changeModelDate
        }

        this.solution_id = 39;
    }

    changeScenarioName(val) {
        this.setState({scenario_name: val});
    }

    changeScenarioDesc(val) {
        this.setState({description: val});
    }

    changeModelDate(val) {
        this.setState({model_date: val});
    }

    changeTab(val){
        if (val <= -1) {
            this.setState({tab: 'setup', category_idx: -1});
        } else if (val >= Object.keys(this.state.inputCategories).length) {
            this.setState({tab: 'review', category_idx: Object.keys(this.state.inputCategories).length})
        } else {
            this.setState({tab: 'category', category_idx: val, category: this.state.inputCategoryOrder[val]});
        }
    }

    postScenario(){
        return fetch('http://'+ window.location.host + '/api/scenario/', {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-CSRFToken': csrf_token
            },
            body: JSON.stringify({name: "Testing", is_adhoc: true, solution: this.solution_id})
        }).then(resp => {
            return resp.json();
        }).then(resp => {
            this.scenario_id = resp.id;
            this.postScenNodeDatas();
        }).catch(err => {
                console.log(err);
        });
    }

    postScenNodeDatas(){
        // Only post data for nodes with changed values
        Object.keys(this.state.nodes).filter(node_id => this.state.nodes[node_id].dirty).map(node_id => {
            let node = this.state.nodes[node_id];
            let node_data_id;
            fetch(`http://${window.location.host}/api/${node.type}-node-data/`, {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrf_token
                },
                body: JSON.stringify({node: node_id, default_data: this.state.nodes[node_id].data, is_model: false})
            }).then(resp => {
                return resp.json();
            }).then(resp => {
                node_data_id = resp.id;
                return fetch(`http://${window.location.host}/api/scen-node/`, {
                    method: 'POST',
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrf_token
                    },
                    body: JSON.stringify({node: node_id, node_data: node_data_id, scenario: this.scenario_id,
                        is_uncertain: false, is_changes: false, is_bounded: false})
                })
            }).catch(err => {
                    console.log(err);
            });
        });
    }

    updateInputNodeData(node_id, layer_idx, nom_idx, val) {
        let newNodes = {...this.state.nodes};
        let newNumDirty = this.state.nodes_changed;
        newNodes[node_id].data[layer_idx][nom_idx] = val;
        if (!newNodes[node_id].dirty) newNumDirty++;
        newNodes[node_id].dirty = true;
        this.setState({nodes: newNodes, nodes_changed: newNumDirty});
    }

    updateConstNodeData(node_id, layer_idx, val){
        let newNodes = {...this.state.nodes};
        let newNumDirty = this.state.nodes_changed;
        newNodes[node_id].data[layer_idx] = val;
        if (!newNodes[node_id].dirty) newNumDirty++;
        newNodes[node_id].dirty = true;
        this.setState({nodes: newNodes, nodes_changed: newNumDirty});
    }

     copyToAllLayers(node_id, layer_idx) {
        let newNodes = {...this.state.nodes};
        let newNumDirty = this.state.nodes_changed;
        let numLayers = newNodes[node_id].data.length;
        for (let layer = 0; layer < numLayers; layer++){
            for (let nom = 0; nom < 5; nom ++) {
                newNodes[node_id].data[layer][nom] = newNodes[node_id].data[layer_idx][nom];
            }
        }
        if (!newNodes[node_id].dirty) newNumDirty++;
        newNodes[node_id].dirty = true;
        this.setState({nodes: newNodes, nodes_changed: newNumDirty});
    }

    fetchNodesBySolution(solution_id){
        // Fetching Nodes
        fetch('http://' + window.location.host + '/api/node/solution=' + solution_id)
            .then(response => {
                return response.json();
            })
            .then(response => {
                let nodes = {};
                let newInputCategoryOrder = [];
                let newInputCategories = {...this.state.inputCategories};
                response.map(node => {
                    // Only include nodes with tags
                    if (node.tags.length > 0) {
                        // Add initial node data to component state
                        let node_obj = {name: node.name, tags: node.tags,
                            visible: true, selectedCategories: {}, dirty: false};
                        Object.keys(this.state.filters).map(cat_id => {
                            node_obj.selectedCategories[cat_id] = true;
                        })
                        nodes[node.id] = node_obj;

                        // Retrieve input category from node if any
                        node.tags.map(tag => {
                            if (tag.includes('CAM_INPUT_CATEGORY==')) {
                                let input_category = tag.substring(tag.lastIndexOf('=')+1, tag.length);
                                if (newInputCategories.hasOwnProperty(input_category)) {
                                    newInputCategories[input_category].push(node.id);
                                } else {
                                    newInputCategories[input_category] = [node.id];
                                    newInputCategoryOrder.push(input_category);
                                }
                            }
                        });
                    }
                });
                newInputCategoryOrder.sort();
                this.setState({nodes: nodes, inputCategories: newInputCategories, inputCategoryOrder: newInputCategoryOrder});
            })
            .catch(err => {
                console.log(err);
            });

        // Fetching NodeDatas for corresponding Nodes
        fetch('http://' + window.location.host + '/api/model-node-data/solution=' + solution_id)
            .then(response => {
                return response.json();
            })
            .then(response => {
                let nodes = {...this.state.nodes};
                // Retrieve Input Nodes
                response.input_nodes.map(node => {
                    if (nodes[node.node] !== undefined) {
                        nodes[node.node].data = node.default_data;
                        nodes[node.node].type = 'input';
                    }
                });
                // Retrieve Const Nodes
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

    filtersBySolution(solution_id) {
        fetch("http://" + window.location.host + "/api/filters/solution=" + solution_id)
            .then(response => {
                return response.json()
            })
            .then(response => {
                let filters = {};
                response.categories.map(category => {
                    filters[category.id] = {name: category.name, options: {}, selected: -1};
                });
                response.options.map(option => {
                    filters[option.category].options[option.id] = {display_name: option.display_name, tag: option.tag};
                });
                this.setState({filters: filters});
            })
            .catch(err => {
                console.log(err);
            })
    }

    componentDidMount() {
        this.filtersBySolution(this.solution_id);
        this.fetchNodesBySolution(this.solution_id);
    }

    onClickSetup() {
        this.setState({tab: 'setup'});
    }

    onClickCategory(e, idx) {
        this.setState({tab: 'category', category_idx: idx, category: this.state.inputCategoryOrder[idx]});
    }

    render() {
        let nodesContext = {nodes: this.state.nodes,
            updateConstNodeData: this.updateConstNodeData,
            updateInputNodeData: this.updateInputNodeData,
            copyToAllLayers: this.copyToAllLayers};
        let pagesContext = {};
        return (
            <React.Fragment>
                <NavBar />
                <NodesContext.Provider value={nodesContext}>
                    <div className="ms-Grid m-t-100" dir="ltr">
                        <div className="ms-Grid-row">
                            <div className="ms-Grid-col ms-md2">
                                <div className="progress-sidebar">
                                    <ScenarioProgressStep index={-1} includeStem={false} changeTab={this.changeTab}
                                                          step={'Setup'} activeStep={this.state.category_idx} />
                                    {this.state.inputCategoryOrder.map((cat_name, index) => {
                                        return (
                                            <ScenarioProgressStep key={`step_${index}`} index={index} includeStem={true} activeStep={this.state.category_idx}
                                                                  changeTab={this.changeTab} step={cat_name.substring(cat_name.indexOf('.')+1, cat_name.length)} />
                                        );
                                    })}
                                    <ScenarioProgressStep index={Object.keys(this.state.inputCategories).length} includeStem={true}
                                                          changeTab={this.changeTab} step={'Review'} activeStep={this.state.category_idx} />
                                </div>
                            </div>
                            <div className="ms-Grid-col ms-md8">
                                {/* Input Category Pages */}
                                {this.state.tab === 'setup' && <SetupPage index={0} changeScenarioName={this.changeScenarioName}
                                                                          changeTab={this.changeTab} {...this.setupProps}
                                                                          name={this.state.scenario_name}
                                                                          desc={this.state.description}
                                                                          date={this.state.model_date} /> }
                                {this.state.tab === 'category' &&
                                    <InputCategoryPage filters={this.state.filters} nodes={this.state.nodes}
                                                       name={this.state.category.substring(this.state.category.indexOf('.')+1, this.state.category.length)}
                                                       index={this.state.category_idx} changeTab={this.changeTab}
                                                       categoryNodes={this.state.inputCategories[this.state.category]} />
                                }
                                {this.state.tab === 'review' && <ReviewPage index={this.state.inputCategoryOrder.length}
                                                                            postScenario={this.postScenario}
                                                                            changeTab={this.changeTab}
                                                                            name={this.state.scenario_name}
                                                                            desc={this.state.description}
                                                                            date={this.state.model_date}
                                                                            nodesChanged={this.state.nodes_changed} />}
                            </div>
                        </div>
                    </div>
                </NodesContext.Provider>
            </React.Fragment>
        );
    }
}

export default ScenarioDefinitionPage;