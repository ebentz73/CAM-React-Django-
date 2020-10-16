import React, {Component} from "react";
import NavBar from "./NavBar";
import HomePageSideBar from "./HomePageSideBar";

class ScenarioHomePage extends Component {
    constructor(props) {
        super(props);
        this.fetchScenariosData = this.fetchScenariosData.bind(this);
    }

    fetchScenariosData() {
        console.log(this.props)
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
                    <HomePageSideBar active="scenario"/>
                    <div className="ms-Grid-col ms-md8 ms-bgColor-gray10">
                        <table className="ms-Table ms-Table--selectable">
                            <thead>
                                <tr>
                                  <th className="ms-fontWeight-bold">Scenarios</th>
                                  <th className="ms-fontWeight-bold">Date</th>
                                  <th className="ms-fontWeight-bold">Status</th>
                                  <th className="ms-fontWeight-bold">Shared</th>
                                </tr>
                            </thead>
                            <tbody>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </React.Fragment>
        );
    }
}

export default ScenarioHomePage;