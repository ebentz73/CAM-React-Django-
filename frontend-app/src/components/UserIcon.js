import React, {Component} from 'react';

class UserIcon extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        return(
            <img className="nav-bar-user" src="/static/frontend-app/transparent-user.jpg"/>
        );
    }
}

export default UserIcon;