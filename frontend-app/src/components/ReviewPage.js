import React, { Component } from "react";
import {
  TextField,
  DatePicker,
  PrimaryButton,
  DefaultButton,
  Stack,
  Text,
} from "@fluentui/react";
import { initializeIcons } from "@fluentui/react";

initializeIcons();

class ReviewPage extends Component {
  constructor(props) {
    super(props);
    this.state = {
      date: props.date,
    };
  }

  componentDidUpdate(prevProps, prevState, snapshot) {
    if (this.props.date !== prevProps.date) {
      //
    }
  }

  render() {
    return (
      <React.Fragment>
        {/* Scenario Info */}
        <div className="scenario-info">
          <TextField
            label="Scenario Name"
            placeholder={this.props.name}
            disabled
          />
          <TextField
            label="Description (Optional)"
            placeholder={this.props.desc}
            disabled
            multiline
            rows={4}
          />
          <DatePicker
            label="Model Start"
            placeholder={this.props.date}
            disabled
          />
          <TextField
            label="Nodes Changed: "
            placeholder={this.props.nodesChanged}
            disabled
          />
          <Stack horizontal>
            <Stack.Item align="start">
              <PrimaryButton
                text="Previous"
                onClick={() => this.props.changeTab(this.props.index - 1)}
              />
            </Stack.Item>
            <Stack.Item align="end">
              <DefaultButton
                text="Save & exit"
                onClick={() => this.props.postScenario(false)}
                disabled={this.props.isReadOnly}
              />
            </Stack.Item>
            <Stack.Item align="end">
              <PrimaryButton
                text="Submit"
                onClick={() => this.props.postScenario(true)}
                disabled={this.props.isReadOnly}
              />
            </Stack.Item>
          </Stack>
        </div>
      </React.Fragment>
    );
  }
}

export default ReviewPage;
