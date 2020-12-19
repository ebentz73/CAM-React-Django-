import React, { Component } from "react";
import { render } from "react-dom";
import { BrowserRouter, Route, Switch } from "react-router-dom";
import ScenarioDefinitionPage from "./ScenarioDefinitionPage";
import PowerBIReport from "./PowerBIReport";
import AnalyticsSolutionPage from "./AnalyticsSolutionPage";
import ScenarioHomePage from "./ScenarioHomePage";
import LoginPage from "./LoginPage";
import PageNotFound from "./PageNotFound";

class App extends Component {
  constructor(props) {
    super(props);
  }

  render() {
    return (
      <React.Fragment>
        <div className="trunav-main">
          <BrowserRouter>
            <Switch>
              <Route
                exact
                path="/frontend-app/solution/:id/new-scenario"
                component={ScenarioDefinitionPage}
              />
              <Route
                exact
                path="/frontend-app/solution/:id/scenario/:scenarioId"
                component={ScenarioDefinitionPage}
              />
              <Route
                exact
                path="/frontend-app/solution/:id/scenario"
                component={ScenarioHomePage}
              />
              <Route
                exact
                path="/frontend-app/home"
                component={AnalyticsSolutionPage}
              />
              <Route
                exact
                path="/frontend-app"
                component={ScenarioDefinitionPage}
              />
              <Route exact path="/frontend-app/login" component={LoginPage} />
              <Route component={PageNotFound} />
            </Switch>
          </BrowserRouter>
        </div>
      </React.Fragment>
    );
  }
}

export default App;

const container = document.getElementById("app");
render(<App />, container);
