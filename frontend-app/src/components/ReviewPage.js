import React, {Component} from "react";
import {TextField, DatePicker, PrimaryButton, Stack} from '@fluentui/react';
import { initializeIcons } from '@fluentui/react';

initializeIcons();


class ReviewPage extends Component {
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
                    <TextField label="Scenario Name" placeholder="Placeholder" disabled />
                    <TextField label="Description (Optional)" multiline rows={4} />
                    <DatePicker label="Model Start" placeholder="Select a date..." />
                    <Stack horizontal horizontalAlign="space-between">
                        <Stack.Item align="start" >
                            <PrimaryButton text="Previous" onClick={() => this.props.changeTab(this.props.index - 1)} />
                        </Stack.Item>
                        <Stack.Item align="end"><PrimaryButton text="Submit" onClick={this.props.postScenario} /></Stack.Item>
                    </Stack>
                </div>
            </div>
        )
    }
}

export default ReviewPage;