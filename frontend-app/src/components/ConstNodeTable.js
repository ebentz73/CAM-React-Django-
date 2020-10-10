import React, {Component} from "react";
import {TextField} from "@fluentui/react";

class ConstNodeTable extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <div className="node-table">
                <table>
                    <tbody>
                        <tr>
                            {this.props.data.map((val, index) => {
                                return (<td key={index}>{val}</td>);
                            })}
                        </tr>
                    </tbody>
                </table>
            </div>
        );
    }
}

export default ConstNodeTable;