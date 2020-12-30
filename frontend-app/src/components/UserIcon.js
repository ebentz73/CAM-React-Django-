import React, { Component } from "react";
import { Persona, PersonaSize, ContextualMenu } from "@fluentui/react";

class UserIcon extends Component {
  constructor(props) {
    super(props);
    this.state = {
      contextMenuShown: false,
      clickPosition: {},
      fullName: "",
      email: "",
    };

    this.onHideContextMenu = this.onHideContextMenu.bind(this);
    this.onShowContextMenu = this.onShowContextMenu.bind(this);
    this.onToggleContextMenu = this.onToggleContextMenu.bind(this);
    this.fetchAllUsers = this.fetchAllUsers.bind(this);
    this.logout = this.logout.bind(this);
  }

  componentDidMount() {
    this.fetchAllUsers();
  }

  logout() {
    const { history } = this.props;
    fetch(`${window.location.protocol}//${window.location.host}/api/logout`)
      .then((response) => {
        console.log(response);
        history.push("/frontend-app/login");
      })
      .catch((error) => {
        console.log(error);
      });
  }

  fetchAllUsers() {
    fetch(`${window.location.protocol}//${window.location.host}/api/user`)
      .then((response) => {
        return response.json();
      })
      .then((response) => {
        const loggedUser = response.filter((user) => user.is_superuser == true);
        const fullName = `${loggedUser[0].first_name} ${loggedUser[0].last_name}`;
        const email = `${loggedUser[0].email}`;
        this.setState({
          fullName,
          email,
        });
      })
      .catch((error) => {
        console.log(error);
      });
  }

  onToggleContextMenu(e) {
    this.setState({
      contextMenuShown: !this.state.contextMenuShown,
      clickPosition: e.target,
    });
  }

  onHideContextMenu() {
    this.setState({ contextMenuShown: false });
  }

  onShowContextMenu() {
    this.setState({ contextMenuShown: true });
  }

  render() {
    const menuItems = [
      {
        key: "username",
        text: `${this.state.fullName}`,
      },
      {
        key: "email",
        text: `${this.state.email}`,
      },
      { key: "logout", text: "Logout", onClick: () => this.logout() },
    ];

    return (
      <div className="nav-bar-user">
        <Persona
          size={PersonaSize.size48}
          onClick={(e) => this.onToggleContextMenu(e)}
        />
        {this.state.contextMenuShown && (
          <ContextualMenu
            items={menuItems}
            target={this.state.clickPosition}
            onItemClick={this.onHideContextMenu}
            onDismiss={this.onHideContextMenu}
            hidden={!this.state.contextMenuShown}
          />
        )}
      </div>
    );
  }
}

export default UserIcon;
