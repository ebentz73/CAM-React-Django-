import React, { Component } from "react";
import UserIcon from "./UserIcon";

class NavBar extends Component {
  constructor(props) {
    super(props);
  }

  render() {
    return (
      <div className="nav-bar">
        <a
          onClick={() => {
            this.props.goHomepage
              ? this.props.goHomepage()
              : (window.location.href = `${window.location.protocol}//${window.location.host}/frontend-app/home`);
          }}
        >
          <img
            className="nav-bar-logo"
            src="https://cdne-cam-dev.azureedge.net/static/frontend-app/lone-star-logo.png"
          />
        </a>
        <UserIcon history={this.props.history} />
        <div style={{ clear: "both" }} />
      </div>
    );
  }
}

export default NavBar;
