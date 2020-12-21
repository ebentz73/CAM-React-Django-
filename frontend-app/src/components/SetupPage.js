import React, { Component } from "react";
import {
  DatePicker,
  Dropdown,
  initializeIcons,
  Position,
  PrimaryButton,
  Slider,
  SpinButton,
  Text,
  TextField,
} from "@fluentui/react";

initializeIcons();

const DayPickerStrings = {
  months: [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
  ],

  shortMonths: [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
  ],

  days: [
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
  ],

  shortDays: ["S", "M", "T", "W", "T", "F", "S"],

  goToToday: "Go to today",
  prevMonthAriaLabel: "Go to previous month",
  nextMonthAriaLabel: "Go to next month",
  prevYearAriaLabel: "Go to previous year",
  nextYearAriaLabel: "Go to next year",
  closeButtonAriaLabel: "Close date picker",
  monthPickerHeaderAriaLabel: "{0}, select to change the year",
  yearPickerHeaderAriaLabel: "{0}, select to change the month",

  isRequiredErrorMessage: "Field is required.",

  invalidInputErrorMessage: "Invalid date format.",
};
class SetupPage extends Component {
  constructor(props) {
    super(props);
    this.state = { inputs: [] };
    this.fetchInputs = this.fetchInputs.bind(this);
  }

  fetchInputs() {
    fetch(
      `${window.location.protocol}//${window.location.host}/api/v1/solutions/${this.props.solutionId}/inputs/`
    )
      .then((response) => response.json())
      .then((response) => {
        this.setState({ inputs: response });
      })
      .catch((err) => {
        console.error(err);
      });
  }

  componentDidMount() {
    this.fetchInputs();
  }

  _getErrorMessage(value) {
    return value === "" ? "Field is required." : "";
  }

  render() {
    return (
      <React.Fragment>
        {/* Scenario Info */}
        <div className="scenario-info">
          <TextField
            label="Scenario Name"
            value={this.props.name !== "" ? this.props.name : "New Scenario"}
            onBlur={(e) => this.props.updateName(e.target.value)}
            required={true}
            onGetErrorMessage={this._getErrorMessage}
            validateOnLoad={false}
            disabled={this.props.isReadOnly}
          />
          <TextField
            label="Description (Optional)"
            defaultValue={this.props.desc}
            multiline
            disabled={this.props.isReadOnly}
            rows={4}
            onBlur={(e) => this.props.updateDesc(e.target.value)}
          />
          <DatePicker
            label="Model Start"
            value={this.props.date}
            onSelectDate={(date) => this.props.updateDate(date)}
            strings={DayPickerStrings}
            isRequired={true}
            disabled={this.props.isReadOnly}
          />
          {this.state.inputs.map((input) => {
            const inputValue = this.props.inputValues[input.id]?.value;
            switch (input.resourcetype) {
              case "InputDataSetInput":
                return (
                  <Dropdown
                    label={input.name}
                    placeHolder="Select an Option"
                    defaultSelectedKey={inputValue}
                    options={input.choices.map((choice) => ({
                      key: choice.id,
                      text: choice.label,
                    }))}
                    key={input.id}
                    onChange={(e, selected) =>
                      this.props.changeInputDataSet(input.id, selected.key)
                    }
                  />
                );
              case "NumericInput":
                return (
                  <SpinButton
                    label={input.name}
                    labelPosition={Position.top}
                    defaultValue={inputValue || 0}
                    min={Number.MIN_SAFE_INTEGER}
                    max={Number.MAX_SAFE_INTEGER}
                    precision={5}
                    key={input.id}
                    onBlur={(e) =>
                      this.props.changeInputs(
                        input.id,
                        input.node,
                        e.target.value
                      )
                    }
                  />
                );
              case "SliderInput":
                return (
                  <Slider
                    label={input.name}
                    defaultValue={
                      inputValue || input.minimum + input.maximum / 2
                    }
                    min={input.minimum}
                    max={input.maximum}
                    step={input.step}
                    key={input.id}
                    onChange={(n) =>
                      this.props.changeInputs(input.id, input.node, n)
                    }
                  />
                );
            }
          })}
          <div className="next-button">
            <PrimaryButton
              text="Next"
              onClick={() => this.props.changeTab(0)}
              disabled={!this.props.date || !this.props.name}
            />
          </div>
        </div>
      </React.Fragment>
    );
  }
}

export default SetupPage;
