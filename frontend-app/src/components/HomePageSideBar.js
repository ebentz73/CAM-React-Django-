import React, { Component } from "react";
import { Link } from "react-router-dom";

class HomePageSideBar extends Component {
  constructor(props) {
    super(props);
  }

  render() {
    return (
      <ul className="ms-List">
        <li className={"ms-ListItem"} tabIndex="0">
          <Link className="withoutUnderline" to="/frontend-app/home">
            <span className="ms-ListItem-secondaryText ms-fontWeight-bold">
              Home
            </span>
          </Link>
        </li>
        {this.props.path !== "" && (
          <li className={"ms-ListItem"}>
            <Link className="withoutUnderline" to={this.props.path}>
              <span className="ms-ListItem-secondaryText">
                Analytics Solution
              </span>
            </Link>
          </li>
        )}
      </ul>
    );
  }
}

export default HomePageSideBar;
