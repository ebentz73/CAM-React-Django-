import React, { Component } from "react";
import { ActionButton, DefaultButton, Breadcrumb } from "@fluentui/react";
import { PowerBIEmbed } from "powerbi-client-react";
import { models } from "powerbi-client";

class PowerBIReport extends Component {
  constructor(props) {
    super(props);
    this.state = {
      embedToken: "",
      embedUrl: "",
      ReportId: "",
    };
    this.fetchReportEmbedData = this.fetchReportEmbedData.bind(this);
    this.downloadResults = this.downloadResults.bind(this);
    this.downloadInputs = this.downloadInputs.bind(this);
    this.clearResults = this.clearResults.bind(this);
  }

  downloadResults() {
    fetch(
      `${window.location.protocol}//${window.location.host}/api/v1/solutions/${this.props.solutionId}/scenarios/${this.props.scenarioId}/export/`
    )
      .then((response) => {
        return response.json();
      })
      .then((response) => {
        console.log(response);
      })
      .catch((err) => {
        console.log(err);
      });
  }

  downloadInputs() {
    console.log("DownloadInputs");
  }

  clearResults() {
    fetch(
      `${window.location.protocol}//${window.location.host}/api/v1/solutions/${this.props.solutionId}/scenarios/${this.props.scenarioId}/reset/`
    )
      .then((response) => {
        return response.json();
      })
      .then((response) => {
        console.log(response);
        this.props.history.push(
          "/frontend-app/solution/" + this.props.solutionId + "/scenario"
        );
      })
      .catch((err) => {
        console.log(err);
      });
  }

  fetchReportEmbedData() {
    fetch(
      `${window.location.protocol}//${window.location.host}/api/v1/solutions/${this.props.solutionId}/powerbi/token`
    )
      .then((response) => {
        return response.json();
      })
      .then((response) => {
        this.setState({
          embedToken: response["embedToken"],
          embedUrl: response["embedUrl"],
          reportId: response["reportId"],
        });
      })
      .catch((err) => {
        console.log(err);
      });
  }

  componentDidMount() {
    this.fetchReportEmbedData();
  }

  render() {
    const itemsWithHref = [
      {
        text: "Analytics Solutions",
        key: "f1",
        onClick: this.props.goHomepage,
      },
      {
        text: `${this.props.solution_name}`,
        key: "f2",
        onClick: this.props.goScenarioListPage,
      },
      { text: `${this.props.scenario_name}`, key: "f3", href: "#" },
    ];

    const menuProps = {
      items: [
        {
          key: "downloadInputs",
          text: "Download Inputs",
          onClick: this.downloadInputs,
        },
        {
          key: "downloadResults",
          text: "Download Results",
          onClick: this.downloadResults,
        },
        {
          key: "clearResults",
          text: "Clear Results",
          onClick: this.clearResults,
        },
      ],
      directionalHintFixed: true,
    };

    return (
      <div>
        <div>
          <div className="result-item">
            <div align="left">
              <ActionButton
                iconProps={{ iconName: "ChevronLeft" }}
                onClick={() => {
                  this.props.history.push(
                    "/frontend-app/solution/" +
                      this.props.solutionId +
                      "/scenario"
                  );
                }}
              >
                Back to Scenarios
              </ActionButton>
            </div>
            <Breadcrumb
              items={itemsWithHref}
              maxDisplayedItems={3}
              ariaLabel="Breadcrumb with items rendered as links"
              overflowAriaLabel="More links"
            />
            <div align="right">
              <DefaultButton
                text="Action"
                menuProps={menuProps}
                allowDisabledFocus
              />
            </div>
          </div>
        </div>
        <PowerBIEmbed
          embedConfig={{
            type: "report", // Supported types: report, dashboard, tile, visual and qna
            id: this.state.reportId,
            embedUrl: this.state.embedUrl,
            accessToken: this.state.embedToken,
            tokenType: models.TokenType.Embed,
            settings: {
              panes: {
                filters: {
                  expanded: false,
                  visible: true,
                },
              },
              background: models.BackgroundType.Transparent,
            },
          }}
          cssClassName={"report-style-class"}
        />
      </div>
    );
  }
}

export default PowerBIReport;
