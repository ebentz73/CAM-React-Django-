import React, { Component } from "react";
import NavBar from "./NavBar";
import { FontIcon, mergeStyles, DefaultButton } from "@fluentui/react";

const iconClass = mergeStyles({
  fontSize: 100,
  height: 100,
  width: 100,
  margin: "0 25px",
});

class PageNotFound extends Component {
  constructor(props) {
    super(props);
  }

  render() {
    return (
      <React.Fragment>
        <div className="nav-bar">
          <a href="/frontend-app/home">
            <img
              className="nav-bar-logo"
              src="https://cdne-cam-dev.azureedge.net/static/frontend-app/lone-star-logo.png"
            />
          </a>
        </div>
        <div className="divider" />
        <div className="ms-Grid grid-margin centered" dir="ltr">
          <div>
            <FontIcon iconName="Warning" className={iconClass} />
            <h1>Page Not Found</h1>
            <DefaultButton
              href={`${window.location.protocol}//${window.location.host}/frontend-app/home`}
            >
              Homepage
            </DefaultButton>
          </div>
        </div>
      </React.Fragment>
    );
  }
}

export default PageNotFound;
