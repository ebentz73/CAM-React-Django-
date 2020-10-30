import React, {Component} from "react";
import UserIcon from './UserIcon'

class NavBar extends Component {
    constructor(props) {
        super(props);
    }

    render(){
        return(
            <div className="nav-bar">
                <img className="nav-bar-logo" src="/static/frontend-app/lone-star-logo.png"/>
                <UserIcon />
                <div style={{clear: 'both'}} />
            </div>
        );
    }
}

export default NavBar;