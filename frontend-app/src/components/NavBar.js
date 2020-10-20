import React, {Component} from "react";

class NavBar extends Component {
    constructor(props) {
        super(props);
    }

    render(){
        return(
            <div className="nav-bar">
                <img className="nav-bar-logo" src="../static/frontend-app/flag-transparent.png"/>
                <img className="nav-bar-user" src="../static/frontend-app/transparent-user.jpg"/>
                <div style={{clear: 'both'}} />
            </div>
        );
    }
}

export default NavBar;