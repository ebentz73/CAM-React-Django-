import React, {Component} from "react";
import NavBar from "./NavBar";
import HomePageSideBar from "./HomePageSideBar";

class AnalyticsSolutionPage extends Component {
    constructor(props) {
        super(props);
        this.state = {
            solutions: [],
        };
        this.fetchAnalyticsSolutionsData = this.fetchAnalyticsSolutionsData.bind(this);
    }

    fetchAnalyticsSolutionsData() {
        fetch("http://" + window.location.host + "/api/solution/")
            .then(response => {
                return response.json()
            })
            .then(response => {
                this.setState({solutions: response})
                console.log(response)
            })
            .catch(err => {
                console.log(err);
            })
    }

    componentDidMount() {
        this.fetchAnalyticsSolutionsData();
    }

    selectSolution(v) {
        window.location = '/frontend-app/solution/' + v + '/scenario';
    }

    render() {
        let selectSolution = this.selectSolution ;

        return (
        <React.Fragment>
            <NavBar />
            <div className="ms-Grid m-t-100" dir="ltr">
                <div className="ms-Grid-row">
                    <HomePageSideBar active="overview"/>
                    <div className="ms-Grid-col ms-md8 ms-bgColor-gray10">
                        <table className="ms-Table ms-Table--selectable">
                            <thead>
                                <tr>
                                  <th className="ms-fontWeight-bold">Model</th>
                                  <th className="ms-fontWeight-bold">Description</th>
                                  <th></th>
                                </tr>
                            </thead>
                            <tbody>

                                {this.state.solutions.map((value, index) => {
                                return <tr onClick={e => this.selectSolution(value['id'])} key={value['id']}><td>{value['name']}</td><td>{value['upload_date']}</td><td> <i className="ms-Icon ms-Icon--ChevronRight" aria-hidden="true"></i> </td></tr>
                              })}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </React.Fragment>
        );
    }
}

export default AnalyticsSolutionPage;