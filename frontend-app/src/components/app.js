import React, {Component} from "react";
import {render} from "react-dom";
import Setup from "./Setup";
import InputCategoryPage from "./InputCategoryPage";

class App extends Component {
    constructor(props) {
        super(props);
        this.state = {
            filters: {},
            phase: 'setup'
        };

        this.onClickOtherPhase = this.onClickOtherPhase.bind(this);
        this.onClickSetup = this.onClickSetup.bind(this);
        this.filtersBySolution = this.filtersBySolution.bind(this);
    }

    filtersBySolution(solution) {
        fetch("http://" + window.location.host + "/api/filters/solution=" + solution)
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
        this.filtersBySolution(31);
    }

    onClickSetup() {
        this.setState({phase: 'setup'});
    }

    onClickOtherPhase() {
        this.setState({phase: 'phase'});
    }

    render() {
        return (
            <div>
                {/* Input Category Pages */}
                <div className="phases">
                    <div onClick={this.onClickSetup}>Setup</div>
                    <div onClick={this.onClickOtherPhase}>Category</div>
                    <div>Submit</div>
                </div>

                {this.state.phase === 'setup' && <Setup /> }
                {this.state.phase === 'phase' && <InputCategoryPage filters={this.state.filters} /> }

            </div>
        );
    }
}

export default App;

const container = document.getElementById("app");
render(<App/>, container);