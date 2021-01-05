import React, { Component } from "react";
import { Persona, PersonaSize, ContextualMenu } from "@fluentui/react";

class UserIcon extends Component {
  constructor(props) {
    super(props);
    this.state = {
      contextMenuShown: false,
      clickPosition: {},
      loggedUser: {},
    };

    this.onHideContextMenu = this.onHideContextMenu.bind(this);
    this.onShowContextMenu = this.onShowContextMenu.bind(this);
    this.onToggleContextMenu = this.onToggleContextMenu.bind(this);
    this.getLoggedUser = this.getLoggedUser.bind(this);
    this.logout = this.logout.bind(this);
  }

  componentDidMount() {
    this.getLoggedUser();
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

  getLoggedUser() {
    const me = JSON.parse(localStorage.getItem("me"));
    this.setState({ loggedUser: me });
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
    const { fullName, email } = this.state.loggedUser;
    const menuItems = [
      {
        key: "fullName",
        text: fullName,
      },
      {
        key: "email",
        text: email,
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
