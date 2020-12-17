import React, { Component } from "react";
import NavBar from "./NavBar";
import HomePageSideBar from "./HomePageSideBar";
import {
  DetailsList,
  DetailsListLayoutMode,
  Selection,
} from "@fluentui/react/lib/DetailsList";
import { Facepile, OverflowButtonType } from "@fluentui/react/lib/Facepile";
import {
  Dialog,
  DialogType,
  DialogFooter,
} from "office-ui-fabric-react/lib/Dialog";
import { PersonaSize } from "@fluentui/react/lib/Persona";
import {
  TextField,
  ActionButton,
  PrimaryButton,
  IIconProps,
} from "@fluentui/react";

const overflowButtonProps = {
  ariaLabel: "More users",
};

function getCookie(name) {
  return (
    (name = (document.cookie + ";").match(new RegExp(name + "=.*;"))) &&
    name[0].split(/=|;/)[1]
  );
}

const csrf_token = getCookie("csrftoken");

class ScenarioHomePage extends Component {
  constructor(props) {
    super(props);
    this.state = {
      scenarios: [],
      columns: [],
      solution_id: null,
      countSelected: 0,
      hideDialog: true,
      firstCheckedScenarioId: null,
      newScenarioName: "",
      selectedScenarios: [],
    };

    this._selection = new Selection({
      onSelectionChanged: (v) => {
        this.selectScenario();
      },
    });
    this._onItemInvoked = (item) => {
      this.props.history.push(
        "/frontend-app/solution/" +
          this.state.solution_id +
          "/scenario/" +
          item["id"].toString()
      );
    };
    this.fetchScenariosData = this.fetchScenariosData.bind(this);
    this._renderItemColumn = this._renderItemColumn.bind(this);
    this.toggleHideDialog = this.toggleHideDialog.bind(this);
    this.onCloneOrMerge = this.onCloneOrMerge.bind(this);
    this.deleteScenario = this.deleteScenario.bind(this);
  }

  deleteScenario() {
    Promise.all(this.state.selectedScenarios.map(scen => {
      return fetch(`${window.location.protocol}//${window.location.host}/api/v1/solutions/`+
            `${this.state.solution_id}/scenarios/${this.state.scenarios[scen].id}/`, {
        method: 'DELETE',
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
          "X-CSRFToken": csrf_token,
        }
      });
    })).then(resp => {
      window.location.reload(false);
    }).catch((err) => {
      console.error(err);
    });
  }
  onCloneOrMerge() {
    if (this.state.countSelected === 1) {
      fetch(
        `${window.location.protocol}//${window.location.host}/api/v1/solutions/`+
          `${this.state.solution_id}/scenarios/${this.state.scenarios[this.state.selectedScenarios[0]].id}/clone/`,
        {
          method: "POST",
          headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
            "X-CSRFToken": csrf_token,
          },
          body: JSON.stringify({
            name: this.state.newScenarioName,
          }),
        }
      ).then(resp => {
        window.location.reload(false);
      }).catch((err) => {
        console.error(err);
      });
    }
    if (this.state.countSelected === 2) {
      fetch(
        `${window.location.protocol}//${window.location.host}/api/v1/solutions/`+
        `${this.state.solution_id}/scenarios/${this.state.scenarios[this.state.selectedScenarios[0]].id}/merge/`,
        {
          method: "POST",
          headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
            "X-CSRFToken": csrf_token,
          },
          body: JSON.stringify({
            name: this.state.newScenarioName,
            mergeId: this.state.scenarios[this.state.selectedScenarios[1]].id,
          }),
        }
      ).then(resp => {
        window.location.reload(false);
      }).catch((err) => {
        console.error(err);
      });

    }
  }

  toggleHideDialog() {
    this.setState((prevState) => ({ hideDialog: !prevState.hideDialog }));
  }

  fetchScenariosData() {
    fetch(
      `${window.location.protocol}//${window.location.host}/api/v1/solutions/${this.props.match.params["id"]}/scenarios`
    )
      .then((response) => {
        return response.json();
      })
      .then((response) => {
        var _columns = [
          {
            key: "scenario",
            name: "Scenario",
            fieldName: "name",
            minWidth: 100,
            maxWidth: 200,
            isResizable: true,
          },
          {
            key: "date",
            name: "Date",
            fieldName: "layer_date_start",
            minWidth: 100,
            maxWidth: 200,
            isResizable: true,
          },
          {
            key: "status",
            name: "Status",
            fieldName: "status",
            minWidth: 100,
            maxWidth: 200,
            isResizable: true,
          },
          {
            key: "shared",
            name: "Shared",
            fieldName: "shared",
            minWidth: 100,
            maxWidth: 200,
            isResizable: true,
          },
        ];
        response.forEach((scenario) => {
          scenario.shared = scenario.shared.map((user) => {
            let firstName = user["first_name"];
            let lastName = user["last_name"];
            let username = user["username"];

            return firstName && lastName
              ? `${firstName.charAt(0)}${lastName.charAt(0)}`
              : username.substring(0, 2);
          });
        });

        this.setState({
          scenarios: response,
          columns: _columns,
          solution_id: this.props.match.params["id"],
        });
      })
      .catch((err) => {
        console.log(err);
      });
  }

  selectScenario() {
    const countSelected = this._selection.getSelectedCount();
    const selectedItem = this._selection.getSelectedIndices();
    this.setState({ firstCheckedScenarioId: selectedItem[0] + 1, selectedScenarios: selectedItem });
    this.setState({ countSelected });
  }

  _renderItemColumn(item, index, column) {
    switch (column.key) {
      case "shared":
        var shared_data = [];
        for (var r in item[column.key]) {
          shared_data.push({ imageInitials: item[column.key][r] });
        }

        var overflowButtonType = OverflowButtonType.descriptive;
        return (
          <Facepile
            personaSize={PersonaSize.size24}
            personas={shared_data}
            maxDisplayablePersonas={2}
            overflowButtonProps={overflowButtonProps}
            overflowButtonType={overflowButtonType}
          />
        );

      default:
        return <span>{item[column.fieldName]}</span>;
    }
  }

  componentDidMount() {
    this.fetchScenariosData();
  }

  render() {
    const path = `/frontend-app/solution/${this.props.match.params["id"]}/scenario`;
    const dialogContentProps = {
      type: DialogType.normal,
      title:
        this.state.countSelected === 1
          ? "Clone Scenario"
          : this.state.countSelected === 2
          ? "Merge Scenario"
          : "",
    };
    return (
      <React.Fragment>
        <NavBar />
        <div className="ms-Grid m-t-100" dir="ltr">
          <div className="ms-Grid-row">
            <div className="ms-Grid-col ms-md3">
              {/* <HomePageSideBar path={path} /> */}
            </div>
            <div className="ms-Grid-col ms-md6">
              <div align="right">
                <ActionButton
                  iconProps={{ iconName: "Add" }}
                  onClick={() => {
                    window.location = `/frontend-app/solution/${this.props.match.params["id"]}/new-scenario`;
                  }}
                >
                  Scenario
                </ActionButton>
              </div>
              <div align="left">
                <ActionButton
                  disabled={this.state.countSelected === 0}
                  iconProps={{ iconName: "RecycleBin" }}
                  onClick={() => {this.deleteScenario()}}
                >
                  Delete
                </ActionButton>
                <ActionButton
                  disabled={this.state.countSelected !== 2}
                  iconProps={{ iconName: "Merge" }}
                  onClick={this.toggleHideDialog}
                >
                  Merge
                </ActionButton>
                <ActionButton
                  disabled={this.state.countSelected !== 1}
                  iconProps={{ iconName: "Copy" }}
                  onClick={this.toggleHideDialog}
                >
                  Clone
                </ActionButton>
              </div>
              <DetailsList
                items={this.state.scenarios}
                columns={this.state.columns}
                setKey="set"
                layoutMode={DetailsListLayoutMode.justified}
                checkButtonAriaLabel="Row checkbox"
                selection={this._selection}
                onRenderItemColumn={this._renderItemColumn}
                onItemInvoked={this._onItemInvoked}
              />
            </div>
          </div>
        </div>
        <Dialog
          hidden={this.state.hideDialog}
          onDismiss={this.toggleHideDialog}
          dialogContentProps={dialogContentProps}
        >
          <TextField
            placeholder="Enter name"
            onBlur={(e) => this.setState({ newScenarioName: e.target.value })}
          />
          <DialogFooter>
            <PrimaryButton text="Save" onClick={this.onCloneOrMerge} />
          </DialogFooter>
        </Dialog>
      </React.Fragment>
    );
  }
}

export default ScenarioHomePage;
