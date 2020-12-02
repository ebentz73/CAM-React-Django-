import React, {Component} from "react";
import {TextField, DatePicker, PrimaryButton, Text} from '@fluentui/react';
import { initializeIcons } from '@fluentui/react';

initializeIcons();


class SetupPage extends Component {
    constructor(props) {
        super(props);
        this.state = {
            //
        }
    }

    componentDidMount() {
        //
    }

    render(){
        return (
            <React.Fragment>
                <Text variant='xLarge'>Setup</Text>
                {/* Scenario Info */}
                <div className="scenario-info">
                    <TextField label="Scenario Name" defaultValue={this.props.name}
                               onBlur={(e) => this.props.updateName(e.target.value)} />
                    <TextField label="Description (Optional)" defaultValue={this.props.desc} multiline rows={4}
                               onBlur={(e) => this.props.updateDesc(e.target.value)} />
                    <DatePicker label="Model Start" defaultValue={this.props.date}
                                onSelectDate={(date) => this.props.updateDate(date)} />
                    <div className="next-button"><PrimaryButton text="Next" onClick={() => this.props.changeTab(0)} /></div>
                </div>
            </React.Fragment>
        )
    }
}

export default SetupPage;