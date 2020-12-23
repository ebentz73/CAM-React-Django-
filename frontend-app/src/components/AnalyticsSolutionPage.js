import React, { Component } from "react";
import NavBar from "./NavBar";
import HomePageSideBar from "./HomePageSideBar";
import {
  DetailsList,
  DetailsListLayoutMode,
  Selection,
} from "@fluentui/react/lib/DetailsList";

class AnalyticsSolutionPage extends Component {
  constructor(props) {
    super(props);
    this._selection = new Selection({
      onSelectionChanged: (v) => {
        this.selectSolution();
      },
    });
    this.state = {
      solutions: [],
      columns: [],
      path: "",
    };
    this.fetchAnalyticsSolutionsData = this.fetchAnalyticsSolutionsData.bind(
      this
    );
  }

  selectSolution() {
    this.setState({
      path:
        "/frontend-app/solution/" +
        this._selection.getSelection()[0]["id"] +
        "/scenario",
    });
    window.location =
      "/frontend-app/solution/" +
      this._selection.getSelection()[0]["id"] +
      "/scenario";
  }

  fetchAnalyticsSolutionsData() {
    fetch(
      `${window.location.protocol}//${window.location.host}/api/v1/solutions/`
    )
      .then((response) => {
        return response.json();
      })
      .then((response) => {
        var _columns = [
          {
            key: "solution",
            name: "Solution",
            fieldName: "name",
            minWidth: 100,
            maxWidth: 200,
            isResizable: true,
          },
          {
            key: "description",
            name: "Description",
            fieldName: "description",
            minWidth: 100,
            maxWidth: 200,
            isResizable: true,
          },
        ];
        this.setState({ solutions: response, columns: _columns });
      })
      .catch((err) => {
        console.log(err);
      });
  }

  componentDidMount() {
    this.fetchAnalyticsSolutionsData();
  }

  render() {
    return (
      <React.Fragment>
        <NavBar />
        <div className="ms-Grid m-t-100" dir="ltr">
          <div className="ms-Grid-row">
            <div className="ms-Grid-col ms-md3">
              {/* <HomePageSideBar path={this.state.path} /> */}
            </div>
            <div className="ms-Grid-col ms-md6">
              <DetailsList
                items={this.state.solutions}
                columns={this.state.columns}
                selection={this._selection}
                setKey="set"
                layoutMode={DetailsListLayoutMode.justified}
                checkButtonAriaLabel="Row checkbox"
                checkboxVisibility={2}
              />
            </div>
          </div>
        </div>
      </React.Fragment>
    );
  }
}

export default AnalyticsSolutionPage;
