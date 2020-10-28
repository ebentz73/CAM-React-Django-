import React, {Component} from "react";

class ScenarioProgressStep extends Component {
    constructor(props) {
        super(props);

        this.state = {
            //
        }
    }

    render() {
        return(
            <React.Fragment>
                {this.props.includeStem &&
                    <div className={`progress-stem ${this.props.index > this.props.activeStep ? 'incomplete-step' : ''}`} />
                }
                <div className="progress-circle-container">
                    <div className={`progress-circle ${this.props.index > this.props.activeStep ? 'incomplete-step' : ''}`}
                         onClick={() => this.props.changeTab(this.props.index)} />
                    <div className={`progress-circle-text ${this.props.index == this.props.activeStep ? 'active-step' : ''}`} >
                        {this.props.step}
                    </div>
                </div>
            </React.Fragment>
        );
    }
}

export default ScenarioProgressStep;