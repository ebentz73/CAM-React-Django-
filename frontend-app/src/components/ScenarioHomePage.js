import React, {Component} from "react";
import NavBar from "./NavBar";
import HomePageSideBar from "./HomePageSideBar";
import { DetailsList, DetailsListLayoutMode, Selection } from '@fluentui/react/lib/DetailsList';
import { Facepile, OverflowButtonType } from '@fluentui/react/lib/Facepile';
import {PersonaSize} from '@fluentui/react/lib/Persona';
import { ActionButton, IIconProps } from '@fluentui/react';

const overflowButtonProps = {
    ariaLabel: 'More users',
  };

class ScenarioHomePage extends Component {
    constructor(props) {
        super(props);
        this.state = {
            scenarios: [],
            columns: [],
            solution_id: null
        };
        this._selection = new Selection({
          onSelectionChanged: (v) => this.selectScenario(),
        });
        this.fetchScenariosData = this.fetchScenariosData.bind(this);
        this._renderItemColumn = this._renderItemColumn.bind(this);
    }

    fetchScenariosData() {
        fetch(`${window.location.protocol}://${window.location.host}/api/solution/${this.props.match.params['id']}/scenario`)
            .then(response => {
                return response.json()
            })
            .then(response => {
                var _columns = [
                  { key: 'scenario', name: 'Scenario', fieldName: 'name', minWidth: 100, maxWidth: 200, isResizable: true },
                  { key: 'date', name: 'Date', fieldName: 'date', minWidth: 100, maxWidth: 200, isResizable: true },
                  { key: 'status', name: 'Status', fieldName: 'status', minWidth: 100, maxWidth: 200, isResizable: true },
                  { key: 'shared', name: 'Shared', fieldName: 'shared', minWidth: 100, maxWidth: 200, isResizable: true },
                ];
                for(var r in response){
                    response[r]['shared'] = ['VT', 'PM', 'SP', 'MV', 'CP', 'CB', 'XY', 'zA']
                }

                this.setState({scenarios: response, columns: _columns, solution_id: this.props.match.params['id']})
            })
            .catch(err => {
                console.log(err);
            })
    }

    selectScenario() {
     this.props.history.push('/frontend-app/solution/' + this.state.solution_id.toString() + '/scenario/' + this._selection.getSelection()[0]['id'].toString())
    }

    _renderItemColumn(item, index, column) {

      switch (column.key) {
        case 'shared':
            var shared_data = []
            for(var r  in item[column.key]){
                shared_data.push({imageInitials: item[column.key][r]})
            }

            var overflowButtonType = OverflowButtonType.descriptive
          return <Facepile
                    personaSize={PersonaSize.size24}
                    personas={shared_data}
                    maxDisplayablePersonas={2}
                    overflowButtonProps={overflowButtonProps}
                    overflowButtonType={overflowButtonType} />

        default:
          return <span>{item[column.fieldName]}</span>;
      }
    }

    componentDidMount() {
        this.fetchScenariosData();
    }

    render() {
        let selectSolution = this.selectSolution ;

        return (
        <React.Fragment>
            <NavBar />
            <div className="ms-Grid m-t-100" dir="ltr">
                <div className="ms-Grid-row">
                    <div className="ms-Grid-col ms-md3">
                        <HomePageSideBar active="overview"/>
                    </div>
                    <div className="ms-Grid-col ms-md6">
                        <div align="right">
                            <ActionButton iconProps={{ iconName: 'Add' }}
                                          onClick={() => {window.location=`/frontend-app/solution/${this.props.match.params['id']}/new-scenario`}}>
                              Scenario
                            </ActionButton>
                        </div>
                        <DetailsList
                            items={this.state.scenarios}
                            columns={this.state.columns}
                            setKey="set"
                            layoutMode={DetailsListLayoutMode.justified}
                            checkButtonAriaLabel="Row checkbox"
                            selection={this._selection}
                            onRenderItemColumn={this._renderItemColumn}
                          />
                    </div>
                </div>
            </div>
        </React.Fragment>

        );
    }
}

export default ScenarioHomePage;