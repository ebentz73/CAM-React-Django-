import React, { Component } from "react";
import { TextField, DatePicker, PrimaryButton, Text } from "@fluentui/react";
import { initializeIcons } from "@fluentui/react";

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
  }

  _getErrorMessage(value) {
    return value === "" ? "Field is required." : "";
  }

  render() {
    return (
      <React.Fragment>
        <Text variant="xLarge">Setup</Text>
        {/* Scenario Info */}
        <div className="scenario-info">
          <TextField
            label="Scenario Name"
            defaultValue={this.props.name ? this.props.name : "New Scenario"}
            onBlur={(e) => this.props.updateName(e.target.value)}
            required={true}
            onGetErrorMessage={this._getErrorMessage}
            validateOnLoad={false}
          />
          <TextField
            label="Description (Optional)"
            defaultValue={this.props.desc}
            multiline
            rows={4}
            onBlur={(e) => this.props.updateDesc(e.target.value)}
          />
          <DatePicker
            label="Model Start"
            value={this.props.date}
            onSelectDate={(date) => this.props.updateDate(date)}
            strings={DayPickerStrings}
            isRequired={true}
          />
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
