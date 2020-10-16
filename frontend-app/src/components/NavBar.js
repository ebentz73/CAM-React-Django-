import React, {Component} from "react";

class NavBar extends Component {
    constructor(props) {
        super(props);
    }

    render(){
        return(
            <div className="nav-bar">
                <img className="nav-bar-logo" src="../static/frontend-app/lone-star-flag.jpg"/>
                <img className="nav-bar-user" src="../static/frontend-app/default-user.png"/>
            </div>
        );
    }
}

export default NavBar;