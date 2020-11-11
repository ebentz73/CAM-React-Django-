import React, {Component} from "react";
import FixedVariableToggle from "./FixedVariableToggle";
import InputNodeTable from "./InputNodeTable";
import ConstNodeTable from "./ConstNodeTable";

class NodeTable extends Component {
    constructor(props) {
        super(props);

        this.state = {
            fixed: false
        }

        this.toggleFixedTableView = this.toggleFixedTableView.bind(this);
    }

    toggleFixedTableView(val) {
        this.setState({fixed: val});
    }

    render() {
        return (
            this.props.nodeId.length > 0 &&
            <React.Fragment>
                <div style={{textAlign: 'right'}} ><FixedVariableToggle toggleFixed={this.toggleFixedTableView} /></div>
                <div className="node-table">
                    <div className="table-scroll-pane">
                        <table className="table-in-scroll-pane">
                            {this.props.type === 'input' ?
                                <InputNodeTable nodeId={this.props.nodeId} data={this.props.data} fixed={this.state.fixed} /> :
                                <ConstNodeTable nodeId={this.props.nodeId} data={this.props.data} fixed={this.state.fixed} />
                            }
                        </table>
                    </div>
                </div>
            </React.Fragment>
        );
    }
}

export default NodeTable;