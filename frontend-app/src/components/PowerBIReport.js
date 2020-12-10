import React, { Component } from "react";
import { ActionButton, DefaultButton, ContextualMenu } from "@fluentui/react";
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
  }

  _onMenuClick(ev) {
    console.log("=========", ev);
  }

  fetchReportEmbedData(solution_id) {
    fetch(
      `${window.location.protocol}//${window.location.host}/api/solution/${this.props.solutionId}/report`
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
    const menuProps = {
      items: [
        {
          key: "downloadInputs",
          text: "Download Inputs",
        },
        {
          key: "downloadResults",
          text: "Download Results",
        },
        {
          key: "clearResults",
          text: "Clear Results",
        },
      ],
      directionalHintFixed: true,
    };

    return (
      <div>
        <div className="result-item">
          <div align="left">
            <ActionButton
              iconProps={{ iconName: "ChevronLeft" }}
              onClick={() => {}}
            >
              Back to Scenarios
            </ActionButton>
          </div>
          <div align="right">
            <DefaultButton
              text="Action"
              menuProps={menuProps}
              onMenuClick={this._onMenuClick}
              allowDisabledFocus
            />
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
                  visible: false,
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
