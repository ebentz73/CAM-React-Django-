import React, {Component} from "react";
import {render} from "react-dom";
import Setup from "./Setup";
import InputCategoryPage from "./InputCategoryPage";
import {PrimaryButton, Stack} from '@fluentui/react';
import {BrowserRouter, Route, Switch} from "react-router-dom";
import ScenarioDefinitionPage from "./ScenarioDefinitionPage";
import PowerBIReport from './PowerBIReport';

class App extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <BrowserRouter>
                <Switch>
                    <Route exact path='/frontend-app/powerbi-report' component={PowerBIReport}/>
                </Switch>
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