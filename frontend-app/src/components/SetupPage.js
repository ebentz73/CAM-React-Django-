import React, {Component} from "react";
import {TextField, DatePicker, PrimaryButton} from '@fluentui/react';
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
            <div>
                {/* Scenario Info */}
                <div className="scenario-info">
                    <TextField label="Scenario Name" onBlur={(e) => this.props.changeScenarioName(e.target.value)} />
                    <TextField label="Description (Optional)" multiline rows={4} />
                    <DatePicker label="Model Start" placeholder="Select a date..." />
                    <div className="next-button"><PrimaryButton text="Next" onClick={() => this.props.changeTab(0)} /></div>
                </div>
            </div>
        )
    }
}

export default SetupPage;