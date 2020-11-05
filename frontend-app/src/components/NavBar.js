import React, {Component} from "react";
import UserIcon from './UserIcon';

class NavBar extends Component {
    constructor(props) {
        super(props);
    }

    render(){
        return(
            <div className="nav-bar">
                <a href='/frontend-app/home'>
                    <img className="nav-bar-logo"
                         src='https://cdne-cam-dev.azureedge.net/static/frontend-app/lone-star-logo.png'/>
                </a>
                <UserIcon />
                <div style={{clear: 'both'}} />
            </div>
        );
    }
}

export default NavBar;