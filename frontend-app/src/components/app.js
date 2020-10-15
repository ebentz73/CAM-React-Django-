import React, {Component} from "react";
import {render} from "react-dom";
import {BrowserRouter, Route, Switch} from "react-router-dom";
import ScenarioDefinitionPage from "./ScenarioDefinitionPage";

class App extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <BrowserRouter>
                <Switch>
                    <Route exact path='/frontend-app' component={ScenarioDefinitionPage}/>
                </Switch>
            </BrowserRouter>
        );
    }
}

export default App;

const container = document.getElementById("app");
render(<App />, container);