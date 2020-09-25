import React, {Component} from "react";
import {render} from "react-dom";
import Setup from "./Setup";
import Phase from "./Phase";

class App extends Component {
    constructor(props) {
        super(props);
        this.state = {
            data: [],
            loaded: false,
            placeholder: "Loading",
            phase: 'setup'
        };

        this.onClickOtherPhase = this.onClickOtherPhase.bind(this);
        this.onClickSetup = this.onClickSetup.bind(this);
    }

    componentDidMount() {
        fetch("/api/evaljob/1")
            .then(response => {
                if (response.status > 400) {
                    return this.setState(() => {
                        return {placeholder: "Something went wrong!"};
                    });
                }
                return response.json();
            })
            .then(data => {
                this.setState(() => {
                    return {
                        data: [data],
                        loaded: true
                    };
                });
            });
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
                {/* Phases */}
                <div className="phases">
                    <div onClick={this.onClickSetup}>Setup</div>
                    <div onClick={this.onClickOtherPhase}>IP Settings</div>
                    <div onClick={this.onClickOtherPhase}>Weather</div>
                    <div onClick={this.onClickOtherPhase}>Submit</div>
                </div>

                {this.state.phase === 'setup' && <Setup /> }
                {this.state.phase === 'phase' && <Phase /> }

            </div>
        );
    }
}

export default App;

const container = document.getElementById("app");
render(<App/>, container);