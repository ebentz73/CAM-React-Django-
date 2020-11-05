import React, {Component} from 'react';
import {Persona, PersonaSize, ContextualMenu} from "@fluentui/react";

class UserIcon extends Component {
    constructor(props) {
        super(props);
        this.state = {
            contextMenuShown: false,
            clickPosition: {}
        }

        this.onHideContextMenu = this.onHideContextMenu.bind(this);
        this.onShowContextMenu = this.onShowContextMenu.bind(this);
        this.onToggleContextMenu = this.onToggleContextMenu.bind(this);
    }

    onToggleContextMenu(e) {
        this.setState({contextMenuShown: !this.state.contextMenuShown, clickPosition: e.target});
    }

    onHideContextMenu() {
        this.setState({contextMenuShown: false});
    }

    onShowContextMenu() {
        this.setState({contextMenuShown: true});
    }

    render() {
        return(
            <div className='nav-bar-user'>
                <Persona size={PersonaSize.size48}
                         onClick={(e) => this.onToggleContextMenu(e)} />
                {this.state.contextMenuShown && <ContextualMenu items={[{key: 'logout', text: 'Logout'}]}
                                                                target={this.state.clickPosition}
                                onItemClick={this.onHideContextMenu} onDismiss={this.onHideContextMenu}
                                hidden={!this.state.contextMenuShown} />}
            </div>

        );
    }
}

export default UserIcon;