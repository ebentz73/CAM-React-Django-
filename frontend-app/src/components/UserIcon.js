import React, {Component} from 'react';
import UserImage from '../../static/frontend-app/transparent-user.jpg';

class UserIcon extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        return(
            <img className="nav-bar-user" src={UserImage}/>
        );
    }
}

export default UserIcon;