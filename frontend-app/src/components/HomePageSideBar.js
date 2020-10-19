import React, {Component} from "react";

class HomePageSideBar extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <div className="ms-Grid-col ms-md2">
                <ul className="ms-List">
                    <li className={"ms-ListItem"} tabIndex="0">
                        <span className="ms-ListItem-secondaryText">Analytics Solution</span>
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
            </div>
        );
    }
}

export default HomePageSideBar;