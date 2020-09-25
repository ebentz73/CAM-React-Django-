import React, {Component} from "react";
import {render} from "react-dom";

class Setup extends Component {
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
                    <div className="node-header">
                        <div className="label">Scenario Name</div>
                        <div className="value">NAMENAME</div>
                    </div>
                    <div>
                        <div className="label">Description</div>
                        <div className="value">NAMENAME</div>
                    </div>
                    <div>
                        <div className="label">Start Date</div>
                        <div className="value">NAMENAME</div>
                    </div>
                </div>

                {/* Other Info */}
                <div className="other-info">
                    <div>Initial IP Count</div>
                    <div>Attrition Rate</div>
                    <div>Growth Rate</div>
                </div>
            </div>
        )
    }
}

export default Setup;