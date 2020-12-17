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
  DefaultButton,
  CommandBarButton,
  Dropdown,
  DropdownMenuItemType,
  IDropdownOption,
  IDropdownStyle,
} from "@fluentui/react";

const overflowButtonProps = {
  ariaLabel: "More users",
};

const dropdownStyles = { dropdown: { width: 300 } };

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
      cloneOrMergeDialog: true,
      shareDialog: true,
      firstCheckedScenarioId: null,
      newScenarioName: "",
      users: [],
      filteredUsers: [],
      sharedScenarioId: "",
      DropdownControlledMultiExampleOptions: [],
      sharedEmails: [],
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
    this.fetchAllUser = this.fetchAllUser.bind(this);
    this._renderItemColumn = this._renderItemColumn.bind(this);
    this.toggleCloneOrMergeDialog = this.toggleCloneOrMergeDialog.bind(this);
    this.toggleShareDialog = this.toggleShareDialog.bind(this);
    this.onCloneOrMerge = this.onCloneOrMerge.bind(this);
    this.sharePeople = this.sharePeople.bind(this);
    this.addPeople = this.addPeople.bind(this);
    this.removeFilteredUser = this.removeFilteredUser.bind(this);
  }

  removeFilteredUser(index) {
    let newArray = [...this.state.filteredUsers];
    newArray.splice(index, 1);
    this.setState({ filteredUsers: newArray });
  }

  _onColumnClickView() {}

  sharePeople() {
    fetch(
      `${window.location.protocol}//${window.location.host}/api/v1/solutions/${this.state.solution_id}/scenarios/${this.state.sharedScenarioId}/`,
      {
        method: "PATCH",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
          "X-CSRFToken": csrf_token,
        },
        body: JSON.stringify({
          // item: 2,
        }),
      }
    ).catch((err) => {
      console.log(err);
    });
  }

  onCloneOrMerge() {
    if (this.state.countSelected === 1) {
      fetch(
        `${window.location.protocol}//${window.location.host}/api/v1/solutions/${this.state.solution_id}/scenarios/${this.state.firstCheckedScenarioId}/clone/`,
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
      ).catch((err) => {
        console.error(err);
      });
    }
    if (this.state.countSelected === 2) {
      fetch(
        `${window.location.protocol}//${window.location.host}/api/v1/solutions/${this.state.solution_id}/scenarios/${this.state.firstCheckedScenarioId}/merge/`,
        {
          method: "POST",
          headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
            "X-CSRFToken": csrf_token,
          },
          body: JSON.stringify({
            name: this.state.newScenarioName,
            mergeId: this.state.firstCheckedScenarioId,
          }),
        }
      ).catch((err) => {
        console.error(err);
      });
    }
  }

  toggleCloneOrMergeDialog() {
    this.setState((prevState) => ({
      cloneOrMergeDialog: !prevState.cloneOrMergeDialog,
    }));
  }

  toggleShareDialog() {
    this.setState((prevState) => ({ shareDialog: !prevState.shareDialog }));
  }

  fetchAllUser() {
    fetch(`${window.location.protocol}//${window.location.host}/api/user`)
      .then((response) => {
        return response.json();
      })
      .then((response) => {
        this.setState({ users: response });
      })
      .catch((error) => {
        console.log(error);
      });
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
          scenario.sharedUserEmail = scenario.shared.map((user) => {
            return user.email;
          });
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
    this.setState({ firstCheckedScenarioId: selectedItem[0] + 1 });
    this.setState({ countSelected });
  }

  addPeople(index, item) {
    this.toggleShareDialog();
    this.setState({ sharedScenarioId: item.id });
    let userEmails = [];
    this.state.users.map((user) => {
      userEmails.push(user.email);
    });

    let DropdownControlledMultiExampleOptions = [];
    let sharedEmails = [...this.state.scenarios[index].sharedUserEmail];
    this.setState({ sharedEmails });
    if (this.state.scenarios[index].sharedUserEmail.length > 0) {
      for (
        let i = 0;
        i < this.state.scenarios[index].sharedUserEmail.length;
        i++
      ) {
        let idx = userEmails.indexOf(
          this.state.scenarios[index].sharedUserEmail[i]
        );
        if (idx > -1) {
          userEmails.splice(idx, 1);
        }
      }
    }

    for (let i = 0; i < userEmails.length; i++) {
      DropdownControlledMultiExampleOptions.push({
        key: `email+${i}`,
        text: userEmails[i],
      });
    }

    this.setState({ DropdownControlledMultiExampleOptions });
  }

  _renderItemColumn(item, index, column) {
    switch (column.key) {
      case "shared":
        var shared_data = [];
        const menuProps = {
          items: [
            {
              key: "addPeople",
              text: "Add People",
              iconProps: { iconName: "Add" },
              onClick: () => this.addPeople(index, item),
            },
          ],
        };
        if (this.state.scenarios[index].sharedUserEmail.length > 0) {
          for (
            let i = 0;
            i < this.state.scenarios[index].sharedUserEmail.length;
            i++
          ) {
            menuProps.items.push({
              key: `email+${i}`,
              text: this.state.scenarios[index].sharedUserEmail[i],
              iconProps: { iconName: "Mail" },
            });
          }
        }

        for (var r in item[column.key]) {
          shared_data.push({ imageInitials: item[column.key][r] });
        }

        var overflowButtonType = OverflowButtonType.descriptive;

        return (
          <div className="share-people">
            <Facepile
              personaSize={PersonaSize.size24}
              personas={shared_data}
              maxDisplayablePersonas={2}
              overflowButtonProps={overflowButtonProps}
              overflowButtonType={overflowButtonType}
            />
            <CommandBarButton
              iconProps={{ iconName: "AddFriend" }}
              menuProps={menuProps}
            ></CommandBarButton>
          </div>
        );

      default:
        return <span>{item[column.fieldName]}</span>;
    }
  }

  componentDidMount() {
    this.fetchScenariosData();
    this.fetchAllUser();
  }

  render() {
    const path = `/frontend-app/solution/${this.props.match.params["id"]}/scenario`;
    const cloneOrMergeDialogContentProps = {
      type: DialogType.normal,
      title:
        this.state.countSelected === 1
          ? "Clone Scenario"
          : this.state.countSelected === 2
          ? "Merge Scenario"
          : "",
    };
    const shareDialogContentProps = {
      type: DialogType.normal,
      title: "Sharing",
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
                  onClick={() => {}}
                >
                  Delete
                </ActionButton>
                <ActionButton
                  disabled={this.state.countSelected !== 2}
                  iconProps={{ iconName: "Merge" }}
                  onClick={this.togglecloneOrMergeDialog}
                >
                  Merge
                </ActionButton>
                <ActionButton
                  disabled={this.state.countSelected !== 1}
                  iconProps={{ iconName: "Copy" }}
                  onClick={this.togglecloneOrMergeDialog}
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
          hidden={this.state.cloneOrMergeDialog}
          onDismiss={this.toggleCloneOrMergeDialog}
          dialogContentProps={cloneOrMergeDialogContentProps}
        >
          <TextField
            placeholder="Enter name"
            onBlur={(e) => this.setState({ newScenarioName: e.target.value })}
          />
          <DialogFooter>
            <PrimaryButton text="Save" onClick={this.onCloneOrMerge} />
          </DialogFooter>
        </Dialog>
        <Dialog
          hidden={this.state.shareDialog}
          onDismiss={this.toggleShareDialog}
          dialogContentProps={shareDialogContentProps}
        >
          <Dropdown
            placeholder="Select options"
            label="Add people"
            // selectedKeys={selectedKeys}
            // onChange={onChange}
            multiSelect
            options={this.state.DropdownControlledMultiExampleOptions}
            styles={dropdownStyles}
          />
          <p>Shared With</p>
          <table>
            <tbody>
              {this.state.sharedEmails.map((sharedEmail, index) => {
                return (
                  <tr key={index}>
                    <td>{sharedEmail}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          <DialogFooter>
            <PrimaryButton text="Save" onClick={this.sharePeople} />
          </DialogFooter>
        </Dialog>
      </React.Fragment>
    );
  }
}

export default ScenarioHomePage;
