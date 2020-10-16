import React, {Component} from "react";
import {render} from "react-dom";
import {BrowserRouter, Route, Switch} from "react-router-dom";
import ScenarioDefinitionPage from "./ScenarioDefinitionPage";
import PowerBIReport from './PowerBIReport';
import AnalyticsSolutionPage from './AnalyticsSolutionPage';
import ScenarioHomePage from './ScenarioHomePage';

class App extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <div>
                <BrowserRouter>
                    <Switch>
                        <Route exact path='/frontend-app/solution/:id/scenario' component={ScenarioHomePage}/>
                    </Switch>
                    <Switch>
                        <Route exact path='/frontend-app/solution/:id/report' component={PowerBIReport}/>
                    </Switch>
                    <Switch>
                        <Route exact path='/frontend-app/home' component={AnalyticsSolutionPage}/>
                    </Switch>
                    <Switch>
                        <Route exact path='/frontend-app' component={ScenarioDefinitionPage}/>
                    </Switch>
                </BrowserRouter>
                <link rel="stylesheet" href="https://static2.sharepointonline.com/files/fabric/office-ui-fabric-js/1.4.0/css/fabric.components.min.css" />
                <link rel="stylesheet" href="https://static2.sharepointonline.com/files/fabric/office-ui-fabric-core/11.0.0/css/fabric.min.css"/>
                <script src="https://static2.sharepointonline.com/files/fabric/office-ui-fabric-js/1.4.0/js/fabric.min.js"></script>
            </div>
        );
    }
}

export default App;

const container = document.getElementById("app");
render(<App />, container);