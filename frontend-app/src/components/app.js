import React, {Component} from "react";
import {render} from "react-dom";
import Setup from "./Setup";
import InputCategoryPage from "./InputCategoryPage";
import {PrimaryButton} from '@fluentui/react';

class App extends Component {
    constructor(props) {
        super(props);
        this.state = {
            filters: {},
            nodes: {},
            tab: 'setup',
            inputCategories: {},
            category: ''
        };

        this.onClickCategory = this.onClickCategory.bind(this);
        this.onClickSetup = this.onClickSetup.bind(this);
        this.filtersBySolution = this.filtersBySolution.bind(this);
        this.fetchNodesBySolution = this.fetchNodesBySolution.bind(this);

        this.solution_id = 34;
    }

    fetchNodesBySolution(solution_id){
        // Fetching Nodes
        fetch('http://' + window.location.host + '/api/node/solution=' + solution_id)
            .then(response => {
                return response.json();
            })
            .then(response => {
                let nodes = {};
                let newInputCategories = {...this.state.inputCategories};
                response.map(node => {
                    // Only include nodes with tags
                    if (node.tags.length > 0) {
                        // Add initial node data to component state
                        let node_obj = {name: node.name, tags: node.tags,
                            visible: true, selectedCategories: {}};
                        Object.keys(this.state.filters).map(cat_id => {
                            node_obj.selectedCategories[cat_id] = true;
                        })
                        nodes[node.id] = node_obj;

                        // Retrieve input category from node if any
                        node.tags.map(tag => {
                            if (tag.includes('CAM_INPUT_CATEGORY:')) {
                                let input_category = tag.substring(tag.indexOf(':')+1, tag.length);
                                if (newInputCategories.hasOwnProperty(input_category)) {
                                    newInputCategories[input_category].push(node.id);
                                } else {
                                    newInputCategories[input_category] = [node.id];
                                }
                            }
                        });
                    }
                });
                this.setState({nodes: nodes, inputCategories: newInputCategories});
            })
            .catch(err => {
                console.log(err);
            });

        // Fetching NodeDatas for corresponding Nodes
        fetch('http://' + window.location.host + '/api/node-data/solution=' + solution_id)
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

    onClickCategory(e, val) {
        this.setState({tab: 'category', category: val});
        console.log(val);
        console.log(this.state.inputCategories);
    }

    render() {
        return (
            <div>
                {/* Input Category Pages */}
                <div className="tabs">
                    <PrimaryButton text="Setup" onClick={this.onClickSetup} />
                    {Object.keys(this.state.inputCategories).map((cat_name, index) => {
                        return (
                            <PrimaryButton key={index} text={cat_name} onClick={(e, val) => this.onClickCategory(e, cat_name)}/>
                        );
                    })}
                    <PrimaryButton text="Submit" />
                </div>

                {this.state.tab === 'setup' && <Setup /> }
                {this.state.tab === 'category' && <InputCategoryPage filters={this.state.filters}
                                                                     nodes={this.state.nodes} category={this.state.inputCategories[this.state.category]}/> }
            </div>
        );
    }
}

export default App;

const container = document.getElementById("app");
render(<App/>, container);