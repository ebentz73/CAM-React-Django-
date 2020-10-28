import React, {Component} from "react";

class HomePageSideBar extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
                <ul className="ms-List">
                    <li className={"ms-ListItem"} tabIndex="0">
                        <span className="ms-ListItem-secondaryText ms-fontWeight-bold">Analytics Solution</span>
                    </li>
                    <li className={"ms-ListItem"}>
                        <ul className="ms-List">
                            <li className={"ms-ListItem " + (this.props.active == 'overview' ? 'is-unread': '')} tabIndex="0">
                                <span className="ms-ListItem-secondaryText">Overview</span>
                            </li>
                            <li className={"ms-ListItem " + (this.props.active == 'scenario'? 'is-unread': '')} tabIndex="0">
                                <span className="ms-ListItem-secondaryText">Scenario</span>
                            </li>
                        </ul>
                    </li>
                </ul>

        );
    }
}

export default HomePageSideBar;