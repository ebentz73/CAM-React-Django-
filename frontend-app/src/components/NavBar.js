import React, {Component} from "react";
import UserIcon from './UserIcon'
import LogoImage from '../../static/frontend-app/lone-star-logo.png';

class NavBar extends Component {
    constructor(props) {
        super(props);
    }

    render(){
        return(
            <div className="nav-bar">
                <img className="nav-bar-logo" src={LogoImage}/>
                <UserIcon />
                <div style={{clear: 'both'}} />
            </div>
        );
    }
}

export default NavBar;